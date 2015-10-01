#!/usr/bin/env bash

# TODO : finish it

PATH=/usr/local/bin/bundle/:$PATH

SERVER_PATH=
cd /var/www/eve_business_server_staging/current


RAILS_ENV=$1 bundle exec /usr/local/bin/bundle/rake data_compute:full:daily >>log/daily.log 2>>log/daily.err

# Tous les heures : on lance le process horaire
15 * * * * cd /var/www/eve_business_server_staging/current; RAILS_ENV=staging /usr/local/bin/bundle/bundle exec /usr/local/bin/bundle/rake data_compute:full:hourly >>log/hourly.log 2>>log/hourly.err
