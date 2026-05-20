# Eve Industrial Tool

A Flask web app for Eve Online industrialists — track market margins, plan manufacturing, and monitor sales orders.

## Features

- **Market overview** — side-by-side sell/buy price cards per trade hub; blueprint table with color-coded margins
- **Production costs** — full batch breakdown (material costs, industry tax, output buy price, margin per unit, craft-vs-sell comparison); nearby buyer/seller order tables
- **My blueprints** — sortable table ranking owned BPCs by batch benefit; tax computed from nearest industry facility
- **Trade hub detail** — sell (p10) and buy (p90) price summary with order depth per station
- **Sales orders** — track your active sell orders and compare against current market prices

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Framework | Flask + SQLAlchemy |
| Database | PostgreSQL (psycopg) |
| Auth | Eve Online SSO (OAuth 2 via ESI) |
| Templates | Jinja2 + Bootstrap 4 |
| Cache | Redis (search autocomplete, 48 h TTL) |

## Setup

```bash
# Install
pip install -e .

# Configure
cp config/config.json.example config/config.json
# → fill in: database_url, esi_client_id, esi_secret_key, secret_key, redis_url

# Migrate
flask db upgrade

# Run
python run.py
```

## Common commands

```bash
# Development server
FLASK_APP=run.py flask run --debug

# Background data processes
python process/hourly.py    # refresh market orders & analytics
python process/daily.py     # refresh price history & production costs
python process/weekly.py    # refresh universe & blueprint data
```

## Architecture

```
evebs/
  __init__.py          app factory
  models/              one file per SQLAlchemy model
    views/             SQL view-backed models (blueprint_costs, legacy views)
  routes/              one Flask Blueprint per resource group
  templates/           Jinja2 templates (shared/ for partials)
  engine/
    routing.py         BFS jump-distance calculator
    industry.py        nearby industry facility finder
  helpers.py           Jinja2 filters: isk, vol, pcent formatters
esi/                   ESI downloaders (orders, assets, universe data)
process/               hourly / daily / weekly orchestration scripts
migrations/            Alembic migration versions
```

### Price columns convention

All price columns are suffixed by order type so the source is always explicit:

| Suffix | Source | Meaning |
|---|---|---|
| `_sell` | `market_seller_prices` p10 | What you pay to acquire (cheapest 10% of sell volume) |
| `_buy` | `market_buyer_prices` p90 | What you receive when selling (strongest 10% of buy volume) |

### Background jobs

- **Hourly** — download region orders → refresh `market_seller_prices` / `market_buyer_prices` materialized views → update buy-order analytics
- **Daily** — download price history → update weekly price details, production costs
- **Weekly** — refresh universe types, blueprints, industry facilities, trade hub flags
