#!/usr/bin/env bash
# Run Flask-Migrate (flask db upgrade) against the main or test database.
#
# Usage:
#   bash scripts/migrate.sh           # migrate main database
#   bash scripts/migrate.sh --test    # migrate test database (evebs_test)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
CONFIG="$ROOT_DIR/config/config.json"

if ! command -v python3 &>/dev/null; then
  echo "python3 is required to parse config.json" >&2
  exit 1
fi

DB_NAME=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['database']['name'])")
DB_USER=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['database']['user'])")
DB_PASS=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['database']['password'])")
DB_HOST=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['database']['host'])")
DB_PORT=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['database']['port'])")

TARGET_DB="$DB_NAME"
for arg in "$@"; do
  [[ "$arg" == "--test" ]] && TARGET_DB="${DB_NAME}_test"
done

DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${TARGET_DB}"

echo "Running migrations against: $TARGET_DB"
cd "$ROOT_DIR"
DATABASE_URL="$DATABASE_URL" flask db upgrade
echo "Done."
