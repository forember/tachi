#!/bin/sh
tar -c -C / -f - \
  srv/ttech.click/htdocs/static \
  etc/lighttpd \
  usr/lib/cgi-bin \
  | tar -x -v -f -
