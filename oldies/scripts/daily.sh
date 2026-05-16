#!/usr/bin/env bash

export EBS_VERBOSE_OUTPUT=true

cd "$(dirname "$BASH_SOURCE")/.."

touch log/daily.log log/daily.err

python process/daily.py >>log/daily.log 2>>log/daily.err

# cat log/daily.log log/daily.err | mail `cat config/email.txt` -s "Evebs daily process"