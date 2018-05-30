#!/bin/bash
cp -f /root/faraday-dev/server.ini /root/.faraday/config
couchdb -b
#./faraday-server.py
python2 ./faraday-server.py --start
#./faraday.py