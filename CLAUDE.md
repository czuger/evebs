# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ground dev rules 

- No commit unless specifically asked for

## Overview

Eve Industrial Tool — a Flask web app for Eve Online players to track market margins, manage production lists, and monitor sales orders.

- **Language**: Python 3
- **Framework**: Flask with SQLAlchemy (PostgreSQL database via psycopg)
- **Auth**: Eve Online SSO (OAuth 2.0 via Eve ESI)
- **Templates**: Jinja2 HTML (Bootstrap 4 via CDN)

## Common Commands

```bash
# Install dependencies
pip install -e .

# Run the development server
python run.py

# Or via Flask
FLASK_APP=run.py flask run --debug

# Background data processes (run via cron in production)
python process/hourly.py
python process/daily.py
python process/weekly.py

# Shell script wrappers (logs to log/)
scripts/hourly.sh
scripts/daily.sh
scripts/weekly.sh
```

## Architecture

### Flask App (`evebs/`)

- **`evebs/__init__.py`**: App factory (`create_app()`). Registers all blueprints and initialises extensions (DB, Redis).
- **`evebs/models/`**: One file per SQLAlchemy model. View-backed models (`BuyOrdersAnalyticsResult`, `PriceAdviceMarginComp`, `PriceAdvicesMinPrice`, `UserSaleOrderDetail`, `ComponentToBuy`) and materialized-view models (`MarketSellerPrice`, `MarketBuyerPrice`) are marked with `__table_args__ = {'info': {'is_view': True}}` — never migrate them.
- **`evebs/helpers.py`**: Jinja2 global helpers (`print_isk`, `print_pcent`, `print_volume`). Format numbers as 1.2B, 34.5M, etc.
- **`evebs/routes/`**: One Blueprint per resource group.
- **`evebs/templates/`**: Jinja2 HTML templates using Bootstrap 4. Shared partials in `shared/`.

### SQL Views (parked)

Five read-only view definitions live in `oldies/sql/sql_views.py` — **not currently active**. The view-backed models in `evebs/models/views.py` still exist but their underlying views need to be reworked before use.

`MarketSellerPrice` and `MarketBuyerPrice` map to PostgreSQL **materialized views** (`market_seller_prices`, `market_buyer_prices`) created in migration `0017`. These are live and refreshed by the hourly process.

### ESI API Layer (`esi/`)

`esi/client.py` — `EsiClient` base class. Handles pagination (`get_all_pages()`), retries on transient errors, and OAuth token refresh for user-authenticated requests. All ESI base URL calls hit `https://esi.evetech.net/latest/`.

Specific downloaders:
- `download_region_orders.py` — public market orders (all regions) → `market_orders`
- `download_history.py` — market price history per region (parallel processes)
- `download_my_orders.py`, `download_my_assets.py` — per-user authenticated downloads
- `update_universe_set_trade_hub.py` — sets `trade_hub=True` on top-volume highsec systems

### Background Processing (`process/`)

Three periodic jobs orchestrated by shell scripts:

**Hourly**: Download region orders → update `buy_orders_analytics`, `prices_advices`

**Daily**: Download market history → update `eve_market_histories_groups`, `weekly_price_details`, item costs, `prices_advices`

**Weekly**: Refresh universe/blueprint/item data

The `process/update_prices.py` module contains all the batch SQL update functions, using `ON CONFLICT ... DO UPDATE SET` (upsert) syntax.

### Redis Cache

`evebs/extensions.py` exposes a module-level `redis_client` initialised in `create_app()`. URL comes from `config/config.json` key `redis_url` (default `redis://localhost:6379/0`). Currently used to cache the `list_items` search dict with a 48 h TTL.

### Authentication

Eve SSO OAuth flow in `evebs/routes/auth.py`. Credentials read from `config/config.json` keys `esi_client_id` / `esi_secret_key`.

### Configuration

`config.py` reads `config/config.json` for Eve SSO credentials, database connection, and Redis URL. Database is PostgreSQL; connection overridable with `DATABASE_URL` env var.

## Key Data Model

- **`UniverseType`** (`universe_types`): An in-game item type sourced from ESI. `cost` and `weekly_avg_price` are computed by the processing pipeline and stored here.
- **`Blueprint`** + **`BlueprintMaterial`**: Crafting recipe → produced `UniverseType` from a list of material `UniverseType`s.
- **`UniverseSystem`** (`universe_systems`): A solar system. Systems with `trade_hub=True` act as market hubs (Jita = id `30000142`, Amarr = `30002187`). Users subscribe to hubs via many-to-many `universe_systems_users`.
- **`User`**: Eve character. Many-to-many with `UniverseType` (items to watch) and `UniverseSystem` (trade hubs).
- **`MarketSellerPrice`** / **`MarketBuyerPrice`**: Materialized views giving the volume-weighted p10 sell price and p90 buy price per `(type_id, system_id)`. Refreshed hourly.
- **`BuyOrdersAnalytic`** / **`PricesAdvice`** / **`WeeklyPriceDetail`**: Per-item/system computed analytics. Updated hourly or daily.

## Configuration Files (not in git)

- `config/config.json` — database connection, Eve SSO client ID and secret, Flask secret key
- `config/email.txt` — recipient for cron process notification emails
