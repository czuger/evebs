FROM postgres:9.6-alpine

#EXPOSE 5433 5432

COPY ./create_users.sh   /docker-entrypoint-initdb.d/10-create_users.sh
COPY ./create_databases.sh     /docker-entrypoint-initdb.d/20-create_dbs.sh

