#!/usr/bin/env bash

docker rm evebs_db
docker run -d -p 5436:5432 --name evebs_db -e POSTGRES_PASSWORD=foo evebs_db
