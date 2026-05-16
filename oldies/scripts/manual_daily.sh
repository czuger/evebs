#!/usr/bin/env bash

RAILS_ENV=production bundle exec rake crontabs:reset

nohup scripts/daily.sh . &
