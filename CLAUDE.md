# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Eve Industrial Tool — a Flask web app for Eve Online players to track market margins, manage production lists, and monitor sales orders.

- **Language**: Python 3
- **Framework**: Flask with SQLAlchemy (SQLite database)
- **Auth**: Eve Online SSO (OAuth 2.0 via Eve ESI)
- **Templates**: Jinja2 HTML (Bootstrap 4 via CDN)

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

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

- **`evebs/__init__.py`**: App factory (`create_app()`). Registers all blueprints, creates DB tables, and creates the 5 SQL views on startup.
- **`evebs/models.py`**: All SQLAlchemy models. View-backed models (`BuyOrdersAnalyticsResult`, `PriceAdviceMarginComp`, `PriceAdvicesMinPrice`, `UserSaleOrderDetail`, `ComponentToBuy`) map to SQL views created at startup — do not migrate them.
- **`evebs/helpers.py`**: Jinja2 global helpers (`print_isk`, `print_pcent`, `print_volume`). Format numbers as 1.2B, 34.5M, etc.
- **`evebs/routes/`**: One Blueprint per resource group.
- **`evebs/templates/`**: Jinja2 HTML templates using Bootstrap 4. Shared partials in `shared/`.

### SQL Views

Five read-only views are created in `evebs/__init__.py:_create_views()` on every app startup (DROP + CREATE). They are SQLite-compatible rewrites of the original PostgreSQL views. The view-backed models have `__table_args__ = {'info': {'is_view': True}}`.

### ESI API Layer (`esi/`)

`esi/client.py` — `EsiClient` base class. Handles pagination (`get_all_pages()`), retries on transient errors, and OAuth token refresh for user-authenticated requests. All ESI base URL calls hit `https://esi.evetech.net/latest/`.

Specific downloaders:
- `download_public_orders.py` — public market orders (all regions)
- `download_history.py` — market price history per region (parallel processes)
- `download_markets_prices.py` — global market adjusted/average prices → `data/cpp_market_prices.yaml`
- `download_my_orders.py`, `download_my_assets.py` — per-user authenticated downloads

### Background Processing (`process/`)

Three periodic jobs orchestrated by shell scripts:

**Hourly**: Download public orders + market prices → update `prices_mins`, `buy_orders_analytics`, `prices_advices`

**Daily**: Download market history → update `eve_market_histories_groups`, `weekly_price_details`, item costs, `prices_advices`

**Weekly**: Refresh universe/blueprint/item data

The `process/update_prices.py` module contains all the batch SQL update functions, using SQLite-compatible `ON CONFLICT ... DO UPDATE SET` (upsert) syntax.

### Authentication

Eve SSO OAuth flow in `evebs/routes/auth.py`. Credentials read from `config/omniauth.yaml` (key `:esi` → `[client_id, secret_key]`) or env vars `ESI_CLIENT_ID` / `ESI_SECRET_KEY`.

### Configuration

`config.py` reads `config/omniauth.yaml` for Eve SSO credentials and sets Flask/SQLAlchemy config. Database is `evebs.db` (SQLite) by default, overridable with `DATABASE_URL` env var.

## Key Data Model

- **`EveItem`**: An in-game item. Has a `slug` for URL-friendly IDs. `cost` field is computed by the processing pipeline.
- **`Blueprint`** + **`BlueprintMaterial`**: Crafting recipe → produced `EveItem` from list of material `EveItem`s.
- **`TradeHub`**: A market location (Jita = `eve_system_id=30000142`, Amarr = `30002187`).
- **`User`**: Eve character. Many-to-many with `EveItem` (items to watch) and `TradeHub`.
- **`PricesMin`** / **`BuyOrdersAnalytic`**: Per-item/hub computed prices. Updated hourly.
- **`PricesAdvice`** / **`WeeklyPriceDetail`**: Longer-term price stats. Updated daily.

## Configuration Files (not in git)

- `config/omniauth.yaml` — Eve SSO client ID and secret (key: `:esi`)
- `config/email.txt` — recipient for cron process notification emails
