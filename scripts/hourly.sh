#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date > log/hourly.log
date > log/hourly.err

RAILS_ENV=production bundle exec rake process:full:hourly >>log/hourly.log 2>>log/hourly.err

cat log/hourly.log log/hourly.err | mail `cat config/email.txt` -s "Evebs staging hourly process"