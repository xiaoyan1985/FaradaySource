#!/bin/bash
cp -f /root/faraday-dev/server.ini /root/.faraday/config
python2 ./faraday-server.py --start
#./faraday.py