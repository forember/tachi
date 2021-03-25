#!/usr/bin/env python3
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 2018 Chris McKinney.

import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.path.append("pydeps")

import cgi
import cgitb
import os
from os import path
from urllib import parse

cgitb.enable(logdir="/var/log/lighttpd/ts1cgi")

STS_HEADER = "Strict-Transport-Security: max-age=31536000"

form = cgi.FieldStorage()

if "test" in form:
    cgi.test()
    import subprocess
    print(subprocess.run("whoami", capture_output=True).stdout)
    raise SystemExit(0)

def error(status, message):
    print("Status: {}".format(status))
    print("Content-Type: text/plain")
    print(STS_HEADER)
    print()
    print("Error: {}".format(message))
    raise SystemExit(0)

host = os.environ.get("HTTP_HOST")
root = path.normpath(path.join("/srv", host, "htdocs"))
if not root.startswith("/srv/"):
    error(500, "invalid host")
url = parse.urlparse(os.environ.get("REQUEST_URI", "")).path
if not url:
    error(500, "no URL?")
pathname = path.normpath(path.join(root, url[1:]))
if not pathname.startswith(root):
    error(500, "invalid path: {} (root: {})".format(pathname, root))
if path.isdir(pathname):
    if path.isfile(path.join(pathname, "index.html")):
        print("Location: {}".format(path.join(url, "index.html")))
        error(301, "Redirecting...")
    elif not url.endswith("/"):
        print("Location: {}/".format(url))
        error(301, "Redirecting...")
    pathname = path.join(pathname, "index")
elif url.endswith("/"):
    print("Location: {}".format(url[:-1]))
    error(301, "Redirecting...")
elif url.endswith("/index"):
    print("Location: {}".format(url[:-5]))
    error(301, "Redirecting...")
elif url.endswith(".ts1"):
    print("Location: {}".format(url[:-4]))
    error(301, "Redirecting...")
if path.isfile(pathname + ".ts1"):
    pathname += ".ts1"
else:
    error(404, "404 Not Found: {}".format(pathname))

print("Content-Type: text/html")
print(STS_HEADER)
print()

import markdown

EXTENSION_LIST = [
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.extra'
        ]
STYLESHEET_FORMAT = '<link rel="stylesheet" type="text/css" href="{}">'

if pathname.endswith(".ts1"):
    import ts1template
    form_dict = {}
    for key in form.keys():
        form_dict[key] = form.getfirst(key)
    mdtext = ts1template.render_template(pathname, _GET=form_dict, _FORM=form)
    print("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>TachibanaSite</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/css/bootstrap.min.css"
              rel="stylesheet"
              integrity="sha384-BmbxuPwQa2lc/FVzBcNJ7UAyJxM6wuqIj61tLrc4wSX0szH/Ev+nYRRuWlolflfl"
              crossorigin="anonymous">
    """)
    stripped = mdtext.strip()
    if stripped.startswith("<!-- LIGHT -->"):
        ts1style_url = "https://ttech.click/static/ts1style.css"
    elif stripped.startswith("<!-- DARK -->"):
        ts1style_url = "https://ttech.click/static/ts1style_dark.css"
    else:
        ts1style_url = "https://ttech.click/static/ts1style_dark.css"
    print(STYLESHEET_FORMAT.format(ts1style_url))
    codehilite_url = "https://ttech.click/static/codehilite.css"
    print(STYLESHEET_FORMAT.format(codehilite_url))
    if "</video-js>" in mdtext:
        videojs_url = "https://vjs.zencdn.net/7.10.2/video-js.css"
        print(STYLESHEET_FORMAT.format(videojs_url))
    deobfuscate_url = "https://ttech.click/static/deobfuscate.js"
    print('<script type="text/javascript" src="{}"></script>'.format(deobfuscate_url))
    print("""
        <link rel="stylesheet" type="text/css"
            href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.10.0/katex.min.css">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/js/bootstrap.bundle.min.js"
                integrity="sha384-b5kHyXgcpbZJO/tY9Ul7kGkf1S0CWuKcCD38l8YkeH8z8QjE0GmW1gYU5S9FOnJ0"
                crossorigin="anonymous"></script>
        <script type="text/javascript"
            src="https://code.jquery.com/jquery-3.3.1.min.js">
        </script>
        <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js">
        </script>
        </script>
        <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.10.0/katex.min.js">
        </script>
        <script type="text/javascript">
            window.addEventListener("load", function(event) {
                $(".katex-math").each(function() {
                    var latex = $(this).text();
                    var html = katex.renderToString(latex);
                    $(this).html(html);
                });
                $(".katex-display").each(function() {
                    var latex = $(this).text();
                    var html = katex.renderToString(latex, {displayMode: true});
                    $(this).html(html);
                });
            });
        </script>
    </head>
    <body>
        <main id="container" class="container" role="main">
            <div id="content" class="markdown-content ts1-content">
    """)
    if not (url == "/" or stripped.endswith("<!-- NOADD -->")):
        print('<p><a href="/">[Home]</a></p>')
    print(markdown.markdown(mdtext, extensions=EXTENSION_LIST))
    if not (stripped.endswith("<!-- NOC -->")
            or stripped.endswith("<!-- NOADD -->")):
        print('<hr><p>&copy; Emberlynn McKinney</p>')
    print("""
            </div>
        </main>
    """)
    if "</video-js>" in mdtext:
        print('<script src="https://vjs.zencdn.net/7.10.2/video.min.js"></script>')
    print("""
    </body>
    </html>
    """)
    raise SystemExit(0)

print("Not Implemented")
