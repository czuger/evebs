#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date > log/weekly.log
date > log/weekly.err

RAILS_ENV=production bundle exec rake process:full:weekly >>log/weekly.log 2>>log/weekly.err

RAILS_ENV=production bundle exec rake -s sitemap:refresh

cat log/weekly.log log/weekly.err | mail `cat config/email.txt` -s "Evebs weekly process"

rm -rf public/items