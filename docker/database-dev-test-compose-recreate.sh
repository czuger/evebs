#!/usr/bin/env bash
docker-compose -f database-dev-compose.yml stop
docker-compose -f database-dev-compose.yml build
docker-compose  -f database-dev-compose.yml up --force-recreate --remove-orphans -d
