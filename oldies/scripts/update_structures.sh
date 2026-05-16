#!/usr/bin/env bash

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

cd $1

date > log/update_structures.log
date > log/update_structures.err

RAILS_ENV=production bundle exec rake data_setup:structures >>log/update_structures.log 2>>log/update_structures.err

cat log/update_structures.log log/update_structures.err | mail `cat config/email.txt` -s "Evebs update_structures"