#!/usr/bin/env bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating database role: dev and test"

$POSTGRES <<-EOSQL
CREATE USER dev WITH CREATEDB PASSWORD 'dev';
CREATE USER test WITH CREATEDB PASSWORD 'test';
EOSQL
