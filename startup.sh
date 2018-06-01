#!/bin/bash
cp -f ./server.ini ../.faraday/config 
chmod 777 ../.faraday/config/server.ini
#cp -f ./config/default.xml ../.faraday/config/config.xml
#chmod 777 ../.faraday/config/config.xml
#couchdb -b
#./faraday-server.py
python2 ./faraday-server.py
python2 ./faraday-server.py --start
python2 ./faraday.py --gui=no-gui --debug