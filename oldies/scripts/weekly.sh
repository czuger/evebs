#!/usr/bin/env bash

export EBS_VERBOSE_OUTPUT=true

cd "$(dirname "$BASH_SOURCE")/.."

python process/weekly.py >>log/weekly.log 2>>log/weekly.err

# cat log/weekly.log log/weekly.err | mail `cat config/email.txt` -s "Evebs weekly process"