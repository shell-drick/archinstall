#!/bin/bash

curl https://raw.githubusercontent.com/shell-drick/archinstall/master/splinter.json -o /root/config.json
curl https://raw.githubusercontent.com/shell-drick/archinstall/master/users.json -o /root/creds.json

archinstall --config /root/config.json --creds /root/creds.json