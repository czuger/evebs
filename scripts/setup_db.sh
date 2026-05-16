#!/usr/bin/env bash
# Creates the PostgreSQL role and database from config/config.json.
# Run once as a user with superuser privileges: bash scripts/setup_db.sh
# Use --test-db to create only the test database (evebs_test) instead.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config/config.json"

CREATE_TEST=false
for arg in "$@"; do
  [[ "$arg" == "--test-db" ]] && CREATE_TEST=true
done

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

if ! $CREATE_TEST; then
  # Create database, offering to drop it first if it already exists
  if $PSQL -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    echo "Database '$DB_NAME' already exists."
    read -r -p "Drop and recreate it? [y/N] " CONFIRM
    if [[ "$(echo "$CONFIRM" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      echo "Dropping database '$DB_NAME'..."
      $PSQL -c "DROP DATABASE $DB_NAME;"
      echo "Creating database '$DB_NAME'..."
      $PSQL -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
      echo "Database recreated."
    else
      echo "Keeping existing database."
    fi
  else
    echo "Creating database '$DB_NAME'..."
    $PSQL -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo "Database created."
  fi

  # Ensure ownership and privileges
  echo "Granting privileges..."
  $PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
  $PSQL -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
fi

if $CREATE_TEST; then
  TEST_DB="${DB_NAME}_test"
  echo ""
  echo "Setting up test database '$TEST_DB'..."
  if $PSQL -tAc "SELECT 1 FROM pg_database WHERE datname='$TEST_DB'" | grep -q 1; then
    echo "Database '$TEST_DB' already exists."
    read -r -p "Drop and recreate it? [y/N] " CONFIRM
    if [[ "$(echo "$CONFIRM" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      echo "Dropping database '$TEST_DB'..."
      $PSQL -c "DROP DATABASE $TEST_DB;"
      echo "Creating database '$TEST_DB'..."
      $PSQL -c "CREATE DATABASE $TEST_DB OWNER $DB_USER;"
      echo "Test database recreated."
    else
      echo "Keeping existing test database."
    fi
  else
    $PSQL -c "CREATE DATABASE $TEST_DB OWNER $DB_USER;"
    echo "Test database created."
  fi
  $PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $TEST_DB TO $DB_USER;"
  $PSQL -d "$TEST_DB" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
fi

echo ""
echo "Done. Run 'bash scripts/migrate.sh' to apply migrations (--test for test DB)."
