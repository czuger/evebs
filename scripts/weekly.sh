#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date >> log/weekly.log
date >> log/weekly.err

RAILS_ENV=production bundle exec rake data_compute:full:weekly >>log/weekly.log 2>>log/weekly.err

date >> log/weekly.log
date >> log/weekly.err

