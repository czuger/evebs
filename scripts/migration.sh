#!/usr/bin/env bash

sqlite3 db/production.sqlite3 .dump | grep -e '"users"' | grep -v 'CREATE' > users.sql
sqlite3 db/production.sqlite3 .dump | grep -e '"identities"' | grep -v 'CREATE' > identities.sql

psql -U eve_business_server_staging eve_business_server < identities.sql
psql -U eve_business_server_staging eve_business_server < users.sql

psql -U eve_business_server_staging eve_business_server < update_sequences.sql