#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date >> log/daily.log
date >> log/daily.err

RAILS_ENV=production bundle exec rake data_compute:full:daily >>log/daily.log 2>>log/daily.err