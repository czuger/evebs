[![Build Status](https://travis-ci.org/czuger/evebs.svg?branch=master)](https://travis-ci.org/czuger/evebs)

# Eve industrial tool

A tool for industrials in Eve Online.

The interface is still in beta, but you can try it here: https://evebs.ieroe.com/

This tool contains:

* Comparison between selling and buying prices and costs (giving you the margin you can expect).
* Tools for handling your production list
* A tool for monitoring your sales orders

## Docker

The stack is defined in [`docker/docker-compose.yml`](docker/docker-compose.yml).

```bash
# Build and start the web app
cd docker
docker compose up app-eve -d --build

# Build the one-shot job images and create their containers WITHOUT starting them
docker compose up app-eve-public-orders app-eve-markets-forecast --build --no-start
```

These are one-shot jobs: each runs a single pass and exits. They are fired periodically by
cron, which just starts the already-created container.

`app-eve-public-orders` (`process/refresh_market_data.py`) refreshes public market data; a
Redis lock skips the run if a previous one is still in progress.

`app-eve-markets-forecast` (`process/refresh_market_forecast.py -d`) downloads fresh market
histories and recomputes the Prophet forecasts.

```cron
*/15 * * * * docker start app-eve-public-orders
0    4 * * * docker start app-eve-markets-forecast
```

## Market forecasting

Forecasting is a two-step pipeline, both reading The Forge (region 10000002) `market_histories`:

1. **`process/compute_prophet_params.py`** analyses each item's price history (volatility,
   trend, outliers, data coverage, a 0-100 reliability score) and stores item-tuned Prophet
   hyper-parameters + a runtime config on `eve_items.prophet_parameters` (JSONB, GIN-indexed).
   Items with fewer than 30 days of history are marked `insufficient_data` and skipped.
2. **`process/refresh_market_forecast.py`** (`-d` first downloads fresh histories) fits Prophet
   for every prophet-ready item using its stored params — applying a log transform when
   `runtime_config.log_transform` is set — and writes the 5-day forecast to
   `market_prophet_forecasts`.

```bash
python process/compute_prophet_params.py     # refresh per-item Prophet params
python process/refresh_market_forecast.py -d # download histories + recompute forecasts
```
