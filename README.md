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
