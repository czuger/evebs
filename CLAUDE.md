# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development rules

- Do not commit unless asked for.
- All imports must be at the top of the file. Never import inside functions, methods, or conditional blocks.
- Avoid local imports. Follow PEP 8.
- NO MONKEYPATCHING EVER
- No broad exception handling — never `except Exception` (or bare `except`). Catch specific exception types (e.g. `EsiError`, `ValueError`).
- Standalone scripts must NOT build the full web app (`from app import app` or `create_app()`). That imports every blueprint, some of which open web log files at import time (e.g. `logs/timings.log`) and fail under a script's user/permissions in production. Instead use `from evebs import create_db_app` and `with create_db_app().app_context(): ...` for DB access, and do not call `setup_logging()` (it also opens `logs/timings.log`); use `set_logger('<script>')` for the script's own dedicated log file.
- When using argparse always add shortcuts for switches (e.g. `--tests` / `-t`).
- Avoid environment variables for runtime config; use script switches instead.
- Always use `alembic revision -m "..."` to generate a new migration.

## Overview

Eve Industrial Tool — a Flask web app for Eve Online players to track market margins, manage production lists, and monitor sales orders.

- **Language**: Python 3
- **Framework**: Flask with SQLAlchemy (PostgreSQL in prod, SQLite for dev/test)
- **Auth**: Eve Online SSO (OAuth 2.0 via Eve ESI)
- **Templates**: Jinja2 HTML (Bootstrap 5.3 via CDN)
- **Redis** is required (used for background job state); configured via `redis_url` in the config JSON.

## Common Commands

```bash
# Install dependencies (app + test)
pip install -r requirements-test.txt

# Run the development server
python app.py
# or
FLASK_APP=app.py flask run --debug

# Run all tests
pytest

# Run a single test file
pytest tests/routes/test_items.py

# Run a single test
pytest tests/routes/test_items.py::TestItemShow::test_200_for_existing_slug

# Run e2e tests (requires `playwright install` first)
pytest tests/e2e/

# Generate a new migration
alembic revision -m "describe the change"

# Apply migrations
alembic upgrade head

# Utility scripts
python scripts/create_user_and_db.py
python scripts/seed_static_data.py
```

## Architecture

### Flask App (`evebs/`)

- **`evebs/__init__.py`**: App factory (`create_app()`). Registers all blueprints and applies `ProxyFix` + `APPLICATION_ROOT` path-stripping middleware. Blueprint imports live *inside* `_register_blueprints()` (a deliberate exception to the imports-at-top rule) so that importing the `evebs` package from a script does not pull in every route module. Also exposes `create_db_app()` — a minimal config+DB-only app for standalone scripts (no blueprints, no route side-effects).
- **`evebs/models/`**: SQLAlchemy models split into subdirectories:
  - `tables/` — regular ORM-mapped tables (one file per model)
  - `views/` — read-only SQL view models (`UserSaleOrderDetail`, `UserIndustryCost`) — do not migrate them; view-backed models carry `__table_args__ = {'info': {'is_view': True}}`
- **`evebs/extensions.py`**: SQLAlchemy `db` and `login_manager` singletons.
- **`evebs/helpers.py`**: Jinja2 globals (`print_isk`, `print_pcent`, `print_volume`) — format ISK numbers as 1.2B, 34.5M, etc.
- **`evebs/utils.py`**: `SimplePagination` helper used by route handlers.
- **`evebs/routes/`**: One Blueprint per resource group, all registered in `create_app()`.
- **`evebs/templates/`**: Jinja2 HTML templates. Shared partials in `shared/`.

### Configuration

`config.py` reads `config/dev_config.json` (development) or `config/production_config.json` (production, `FLASK_ENV=production`). Database defaults to SQLite (`evebs.db`) when no `host` key is present, otherwise PostgreSQL. Setting `EVEBS_TEST_DB=1` appends `_test` to the DB name (handled automatically by `tests/conftest.py`).

Logging: `setup_logging()` writes JSON to `logs/evebs.log` (daily rotation, 30-day retention) and plain text to stdout. `set_logger(name)` creates an isolated named logger writing to `logs/<name>.log`.

Config files (not in git):
- `config/dev_config.json` — copy from `dev_config.json.example`
- `config/production_config.json` — copy from `production_config.json.example`

### ESI API Layer (`esi/`)

`esi/client.py` — `EsiClient` base class with pagination (`get_all_pages()`), retry on transient errors, and OAuth token refresh for authenticated requests. All calls hit `https://esi.evetech.net/latest/`.

Downloaders:
- `download_public_orders/` — package; downloads public market orders for all regions
- `download_market_histories.py` — downloads exact ESI market history per region/type (`/types` enumerates type_ids, `/history` fetched per type) into `market_histories`; `-f/--forge` restricts to The Forge
- `download_markets_prices.py` — global adjusted/average prices
- `download_universe_regions.py` — region/constellation/system hierarchy
- `download_universe_stations.py`, `download_universe_structures.py` — station and structure data
- `download_my_orders.py`, `download_my_assets.py`, `download_my_blueprints.py`, `download_my_industry_jobs.py` — per-user authenticated downloads

### Background Processing (`process/`)

Standalone scripts (no longer orchestrated by hourly/daily/weekly wrappers):

- `orders_daemon.py` — long-running daemon; downloads public orders every 15 min, runs `update_jita_market_analytics` after each pass. Trade-hub regions every pass; all regions every 4th pass.
- `update_blueprints.py` — upserts `Blueprint` rows from `data/manufacturing_tree.json` and computes `manufacturing_cost` from current Jita prices.
- `update_jita_market_analytics.py` — updates `jita_market_analytics` table (P10 Jita sell price + 3-day volume-weighted price forecast).
- `update_public_orders.py` — standalone public order download + price update.
- `sync_assets.py` — syncs user blueprint/asset data from ESI.

### Data Pipeline (`data/`)

`data/build_manufacturing_tree.py` reads raw EVE SDE files from `data/eve_static_data/` and produces `data/manufacturing_tree.json` — a recursive bill-of-materials tree for all manufacturing and reaction blueprints. `process/update_blueprints.py` consumes this file to populate the DB.

### Authentication

Eve SSO OAuth flow in `evebs/routes/auth.py`. Credentials from config JSON under `esi.client_id` / `esi.secret_key`.

## Key Data Model

- **`EveItem`**: An in-game item. `slug` is used for URL-friendly IDs. `base_item=True` marks raw materials.
- **`Blueprint`**: Crafting recipe. Key fields: `produced_type_id`, `nb_runs`, `prod_qtt`, `activity_type` (`manufacturing`/`reaction`/etc.), `manufacturing_cost`, and `manufacturing_tree` (JSON — recursive BOM, top-level keys are direct materials used in cost calculation; nested `chain` is for display only).
- **`BlueprintModification`**: Per-user ME/TE bonuses on a blueprint.
- **`UniverseSystem`**: Solar system. `trade_hub=True` marks market hubs; Jita is system ID `30000142`.
- **`UniverseRegion` / `UniverseConstellation` / `UniverseSystem` / `UniverseStation` / `UniverseStructure` / `UnknownStructure`**: Full universe hierarchy.
- **`User`**: Eve character. JSON columns: `buy_order_filtering`, `sell_orders_filtering`, `industry_taxes` (per-activity SCI/SCC/structure tax rates in plain %), `sales_taxes` (broker fee, sales tax, safety margin). Many-to-many with `EveItem` (watched items), `UniverseSystem` (trade hubs), `Blueprint` (owned blueprints).
- **`PublicTradeOrder`**: Live market orders downloaded from ESI.
- **`SalesFinal`**: Historical completed sales at Jita (source for `price_forecast_3d`).
- **`UserSaleOrder`**: User's own active sell orders.
- **`BpcAsset` / `BpcAssetsStation`**: Blueprint copy assets per user/station.
- **`ProductionList` / `InventionList` / `CopyList`**: User production planning lists.
- **`IndustryJob`**: Active industry jobs downloaded from ESI.
- **`JitaMarketAnalytics`**: Regular table (not a materialized view) — one row per item type. `min_sell_price` (P10 ask) + `price_forecast_3d` (volume-weighted 3-day forecast). Updated by `process/update_jita_market_analytics.py`.
- **`BuyOrdersAnalytic`**: Per-item/hub computed buy-order analytics.
- **`EveItemsSavedList`**: User-saved item ID lists (JSON column).
- **`LastUpdate`**: Process heartbeat timestamps.
- **SQL views** (`UserSaleOrderDetail`, `UserIndustryCost`): defined in migrations, never migrated directly.

## Tests

Tests live under `tests/` mirroring the source layout: `tests/routes/`, `tests/esi/`, `tests/process/`, `tests/templates/`, `tests/e2e/`, `tests/scripts/`.

`tests/conftest.py` sets `EVEBS_TEST_DB=1` before any import, creates a session-scoped app, and truncates all non-view tables before each test via `_truncate` (autouse). Key fixtures: `db`, `client`, `user`, `admin_user`, `auth_client`, `admin_client`.

`tests/factories.py` contains simple factory helpers (`make_item`, `make_blueprint`, `make_universe_system`, `make_trade_hub`, etc.) that take a live `db` and return flushed (not committed) objects.

E2E tests (`tests/e2e/`) use Playwright with a live Werkzeug server on port 5099. The `auth_page` fixture injects a session cookie to bypass SSO. Install Playwright browsers once with `playwright install`.
