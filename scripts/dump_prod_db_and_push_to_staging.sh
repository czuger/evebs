#!/usr/bin/env bash

pg_dump -Fc -n public -U eve_business_server eve_business_server_production -f /tmp/production.dump

scp /tmp/production.dump dw:/tmp/production.dump