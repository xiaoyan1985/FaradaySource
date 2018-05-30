#!/bin/bash
cp -f ./server.ini /root/.faraday/config
chmod 777 /root/.faraday/config/server.ini
couchdb -b
#./faraday-server.py
python2 ./faraday-server.py --start
#./faraday.py