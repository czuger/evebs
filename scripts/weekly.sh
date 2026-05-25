#!/usr/bin/env bash

cd "$(dirname "$BASH_SOURCE")/.."

python process/weekly.py --verbose >>log/weekly.log 2>>log/weekly.err

# cat log/weekly.log log/weekly.err | mail `cat config/email.txt` -s "Evebs weekly process"