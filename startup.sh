#!/bin/bash
git pull
cp -f ./server.ini ../.faraday/config 
chmod 777 ../.faraday/config/server.ini
python2 ./faraday-server.py
