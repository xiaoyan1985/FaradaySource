#!/bin/bash
cp -f ./user.xml ../.faraday/config 
chmod 777 ../.faraday/config/user.xml
python2 ./faraday.py --gui=no-gui
