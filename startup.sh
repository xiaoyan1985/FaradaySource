#!/bin/bash
couchdb -b
./faraday-server.py
python2 ./faraday-server.py --start
