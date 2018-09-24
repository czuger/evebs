#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

RAILS_ENV=production bundle exec rake -s sitemap:refresh