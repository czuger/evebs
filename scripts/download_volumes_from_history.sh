#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date > log/update_volumes_from_history.log
date > log/update_volumes_from_history.err

RAILS_ENV=production bundle exec rake process:update_volumes_from_history >>log/update_volumes_from_history.log 2>>log/update_volumes_from_history.err

cat log/update_volumes_from_history.log log/update_volumes_from_history.err | mail `cat config/email.txt` -s "Evebs update_volumes_from_history"