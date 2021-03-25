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
import requests

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

try:
    r = requests.get("http://localhost:5000/team", params={"poke": form.getlist("poke")})
except Exception as e:
    error(500, str(e))

print("Content-Type: application/json")
print(STS_HEADER)
print()
print(r.text)
