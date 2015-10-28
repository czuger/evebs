#!/usr/bin/env bash

PATH=/usr/local/bin/:$PATH

# All the rake tasks to be executed monthly
RAILS_ENV=production bundle exec rake data_compute:price_history:update:monthly >>log/monthly.log

