#!/usr/bin/env bash

../bin/rails db:environment:set RAILS_ENV=test

export RAILS_ENV=test

bundle exec rake db:drop
bundle exec rake db:create
bundle exec rake db:migrate

