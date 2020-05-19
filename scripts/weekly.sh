#!/usr/bin/env bash

export EBS_VERBOSE_OUTPUT=true

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd "`dirname $BASH_SOURCE`/.."

bundle exec rake process:full:weekly >>log/weekly.log 2>>log/weekly.err

# Already ran in process:full:weekly
#bundle exec rake -s sitemap:refresh

# cat log/weekly.log log/weekly.err | mail `cat config/email.txt` -s "Evebs weekly process"

rm -rf public/items