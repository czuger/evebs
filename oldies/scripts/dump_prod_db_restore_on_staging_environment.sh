#!/usr/bin/env bash

dropdb eve_business_server_staging
createdb eve_business_server_staging

pg_restore --no-owner -d eve_business_server_staging -n public /tmp/production.dump