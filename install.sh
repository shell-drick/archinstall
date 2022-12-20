#!/bin/bash

curl https://raw.githubusercontent.com/shell-drick/archinstall/master/splinter.json -o /root/config.json
curl https://raw.githubusercontent.com/shell-drick/archinstall/master/creds.json -o /root/creds.json

archinstall --config /root/config.json --creds /root/creds.json