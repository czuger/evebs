#!/usr/bin/env bash

sqlite3 ../db/production.sqlite3 .dump | grep -e '"users"' | grep -v 'CREATE' > users.sql
sqlite3 ../db/production.sqlite3 .dump | grep -e '"identities"' | grep -v 'CREATE' > identities.sql

psql -U eve_business_server eve_business_server_staging < identities.sql
psql -U eve_business_server eve_business_server_staging < users.sql

psql -U eve_business_server eve_business_server_staging < update_sequences.sql
