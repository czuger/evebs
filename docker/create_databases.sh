#!/usr/bin/env bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating databases: dev and test"

$POSTGRES <<EOSQL
CREATE DATABASE dev OWNER dev;
CREATE DATABASE test OWNER test;
EOSQL