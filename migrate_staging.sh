sqlite3 db/production.sqlite3 .dump | grep -e '"users"' | grep -v 'CREATE' > tmp/users.sql
sqlite3 db/production.sqlite3 .dump | grep -e '"identities"' | grep -v 'CREATE' > tmp/identities.sql

psql -U eve_business_server eve_business_server_staging < tmp/identities.sql
psql -U eve_business_server eve_business_server_staging < tmp/users.sql
