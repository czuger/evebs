#!/usr/bin/env bash

PATH=/usr/local/bin/:$PATH

# All the rake tasks to be executed weekly
RAILS_ENV=production bundle exec rake data_compute:min_prices:all >>log/weekly.log

