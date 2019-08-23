#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd "`dirname $BASH_SOURCE`/.."

bundle exec rake process:full:hourly >>log/hourly.log 2>>log/hourly.err

# cat log/hourly.log log/hourly.err | mail `cat config/email.txt` -s "Evebs hourly process"

bundle exec rake maintenance:check_working_hourly_process >>log/check_working_hourly_process.log 2>>log/check_working_hourly_process.err

rm -rf public/market_data