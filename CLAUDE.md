# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development rule

- Do not commit unless asked for.
- Avoid local import. Basically follow PEP 8 – Style Guide for Python Code
- NO MONKEYPATCHING EVER
- when using argparse allways use shortcuts for switches (if you add --tests also add -t for instance)
- avoid system variable, use script switches instead
- Always use alembic revision -m "..." to generate a new migration 


## Overview

Eve Industrial Tool — a Flask web app for Eve Online players to track market margins, manage production lists, and monitor sales orders.

- **Language**: Python 3
- **Framework**: Flask with SQLAlchemy (PostgreSQL database)
- **Auth**: Eve Online SSO (OAuth 2.0 via Eve ESI)
- **Templates**: Jinja2 HTML (Bootstrap 5.3 via CDN)

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py

# Or via Flask
FLASK_APP=app.py flask run --debug

# Background data processes (run via cron in production)
python process/hourly.py
python process/daily.py
python process/weekly.py

# Utility scripts
python scripts/create_user_and_db.py
python scripts/seed_static_data.py

# Run tests
pytest
```

## Architecture

### Flask App (`evebs/`)

- **`evebs/__init__.py`**: App factory (`create_app()`). Registers all blueprints and applies `ProxyFix` + `APPLICATION_ROOT` middleware.
- **`evebs/models/`**: SQLAlchemy models split into three subdirectories:
  - `tables/` — regular ORM-mapped tables (one file per model)
  - `views/` — read-only SQL view models (`BuyOrdersAnalyticsResult`, `PriceAdviceMarginComp`, `PriceAdvicesMinPrice`, `UserSaleOrderDetail`, `ComponentToBuy`) — do not migrate them
  - `materialized_views/` — PostgreSQL materialized views (`JitaPrices`, `JitaManufacturingMargins`) — refreshed by process scripts via `REFRESH MATERIALIZED VIEW`
- **`evebs/extensions.py`**: SQLAlchemy `db` and `login_manager` instances.
- **`evebs/helpers.py`**: Jinja2 global helpers (`print_isk`, `print_pcent`, `print_volume`). Format numbers as 1.2B, 34.5M, etc.
- **`evebs/routes/`**: One Blueprint per resource group.
- **`evebs/templates/`**: Jinja2 HTML templates using Bootstrap 5.3. Shared partials in `shared/`.

### SQL Views

Five read-only SQL views (`evebs/models/views/`) and two materialized views (`evebs/models/views/materialized_views/`) are defined in migrations. View-backed models have `__table_args__ = {'info': {'is_view': True}}`.

### ESI API Layer (`esi/`)

`esi/client.py` — `EsiClient` base class. Handles pagination (`get_all_pages()`), retries on transient errors, and OAuth token refresh for user-authenticated requests. All ESI base URL calls hit `https://esi.evetech.net/latest/`.

Specific downloaders:
- `download_public_orders/` — public market orders (package, all regions)
- `download_history.py` — market price history per region (parallel processes)
- `download_markets_prices.py` — global market adjusted/average prices
- `download_universe_regions.py` — universe region/constellation/system/station hierarchy
- `download_my_orders.py`, `download_my_assets.py`, `download_my_blueprints.py` — per-user authenticated downloads

### Background Processing (`process/`)

Three periodic jobs orchestrated by shell scripts:

**Hourly**: Download public orders + market prices → update `prices_mins`, `buy_orders_analytics`, `prices_advices`

**Daily**: Download market history → update `eve_market_histories_groups`, `weekly_price_details`, item costs, `prices_advices`

**Weekly**: Refresh universe data (`DownloadUniverseRegions`)

Additional standalone scripts:
- `update_jita_prices.py` — `REFRESH MATERIALIZED VIEW jita_prices`
- `update_jita_manufacturing_margins.py` — `REFRESH MATERIALIZED VIEW jita_manufacturing_margins`
- `update_blueprints.py`, `update_costs.py`, `update_eve_item_costs.py`, `update_public_orders.py`
- `orders_daemon.py` — long-running orders watch daemon

The `process/update_prices.py` module contains batch SQL update functions using `ON CONFLICT ... DO UPDATE SET` (upsert) syntax.

### Authentication

Eve SSO OAuth flow in `evebs/routes/auth.py`. Credentials read from `config/dev_config.json` or `config/production_config.json` (key `esi` → `client_id`, `secret_key`).

### Configuration

`config.py` reads `config/dev_config.json` (development) or `config/production_config.json` (production, when `FLASK_ENV=production`) for Eve SSO credentials and DB settings. Database defaults to SQLite (`evebs.db`) if no `host` is set in the config, otherwise uses PostgreSQL. Set `EVEBS_TEST_DB=1` to use the test database.

Logging: `setup_logging()` in `config.py` writes JSON logs to `logs/evebs.log` (daily rotation, 30-day retention) and plain-text to stdout.

## Key Data Model

- **`EveItem`**: An in-game item. Has a `slug` for URL-friendly IDs. `cost` field is computed by the processing pipeline.
- **`Blueprint`** + **`BlueprintMaterial`** + **`BlueprintModification`**: Crafting recipe → produced `EveItem` from list of material `EveItem`s.
- **`UniverseSystem`**: A solar system. `trade_hub=True` marks it as a market hub (Jita `cpp_system_id=30000142`, Amarr `30002187`). Replaces the old `TradeHub` model.
- **`UniverseRegion` / `UniverseConstellation` / `UniverseSystem` / `UniverseStation` / `UniverseStructure`**: Full universe hierarchy downloaded from ESI.
- **`User`**: Eve character. Many-to-many with `EveItem` (items to watch) and `UniverseSystem` (trade hubs, via `trade_hubs_users`).
- **`PricesMin`** / **`BuyOrdersAnalytic`**: Per-item/hub computed prices. Updated hourly.
- **`PricesAdvice`** / **`WeeklyPriceDetail`**: Longer-term price stats. Updated daily.
- **`BpcAsset`** / **`BpcAssetsStation`**: Blueprint copy assets per user/station.
- **`Crontab`** / **`LastUpdate`**: Process heartbeats and last-run timestamps.
- **`JitaPrices`** / **`JitaManufacturingMargins`**: PostgreSQL materialized views for Jita trading/manufacturing analysis.

## Configuration Files (not in git)

- `config/dev_config.json` — development credentials (copy from `dev_config.json.example`)
- `config/production_config.json` — production credentials (copy from `production_config.json.example`)
- `config/email.txt` — recipient for cron process notification emails
