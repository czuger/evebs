#!/usr/bin/env bash

cd "$(dirname "$BASH_SOURCE")/.."

touch log/daily.log log/daily.err

python process/daily.py --verbose --essentials >>log/daily.log 2>>log/daily.err

# cat log/daily.log log/daily.err | mail `cat config/email.txt` -s "Evebs daily process"