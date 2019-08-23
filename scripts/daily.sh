#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd "`dirname $BASH_SOURCE`/.."

touch log/daily.log log/daily.err

bundle exec rake process:full:daily >>log/daily.log 2>>log/daily.err

# cat log/daily.log log/daily.err | mail `cat config/email.txt` -s "Evebs daily process"

rm -rf public/production_costs