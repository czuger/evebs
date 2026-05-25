#!/usr/bin/env bash

cd "$(dirname "$BASH_SOURCE")/.."

python process/hourly.py >>log/hourly.log 2>>log/hourly.err

# cat log/hourly.log log/hourly.err | mail `cat config/email.txt` -s "Evebs hourly process"