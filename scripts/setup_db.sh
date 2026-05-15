#!/usr/bin/env bash
# Creates the PostgreSQL role and database from config/config.json.
# Run once as a user with superuser privileges: bash scripts/setup_db.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config/config.json"

if ! command -v python3 &>/dev/null; then
  echo "python3 is required to parse config.json" >&2
  exit 1
fi

DB_NAME=$(python3 -c "import json,sys; c=json.load(open('$CONFIG')); print(c['database']['name'])")
DB_USER=$(python3 -c "import json,sys; c=json.load(open('$CONFIG')); print(c['database']['user'])")
DB_PASS=$(python3 -c "import json,sys; c=json.load(open('$CONFIG')); print(c['database']['password'])")
DB_HOST=$(python3 -c "import json,sys; c=json.load(open('$CONFIG')); print(c['database']['host'])")
DB_PORT=$(python3 -c "import json,sys; c=json.load(open('$CONFIG')); print(c['database']['port'])")

echo "Setting up PostgreSQL:"
echo "  host:     $DB_HOST:$DB_PORT"
echo "  database: $DB_NAME"
echo "  user:     $DB_USER"
echo ""

PSQL="psql -h $DB_HOST -p $DB_PORT -U postgres"

# Create role if it doesn't exist
if $PSQL -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
  echo "Role '$DB_USER' already exists — skipping creation."
else
  echo "Creating role '$DB_USER'..."
  $PSQL -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
  echo "Role created."
fi

# Create database if it doesn't exist
if $PSQL -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  echo "Database '$DB_NAME' already exists — skipping creation."
else
  echo "Creating database '$DB_NAME'..."
  $PSQL -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
  echo "Database created."
fi

# Ensure ownership and privileges
echo "Granting privileges..."
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
$PSQL -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

echo ""
echo "Done. Run 'flask db upgrade' to apply migrations."
