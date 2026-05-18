# Data models

All models live in `evebs/models/`. SQLAlchemy + PostgreSQL. Timestamps (`created_at`, `updated_at`) are omitted from column tables below unless notable.

---

## Table of contents

1. [Universe hierarchy](#1-universe-hierarchy)
2. [Market](#2-market)
3. [Pricing & analytics](#3-pricing--analytics)
4. [Production](#4-production)
5. [User & assets](#5-user--assets)
6. [Infrastructure](#6-infrastructure)
7. [SQL views (read-only)](#7-sql-views-read-only)
8. [Association tables](#8-association-tables)

---

## 1. Universe hierarchy

Static data imported from the ESI API. Reflects the in-game geographic and item taxonomy. Updated infrequently (weekly process).

### `UniverseRegion` — `universe_regions`
Top-level geographic unit. Contains constellations; some regions host trade hubs.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `region_id` |
| `name` | Text | |
| `description` | Text | |

**Relationships:** `universe_constellations`, `trade_hubs`, `eve_market_histories_groups`

---

### `UniverseConstellation` — `universe_constellations`
Groups several solar systems within a region.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `constellation_id` |
| `universe_region_id` | BigInt FK | → `universe_regions.id` |
| `name` | Text | |

**Relationships:** `universe_region`, `universe_systems`

---

### `UniverseSystem` — `universe_systems`
A solar system. Central hub for routing, market orders, and industry cost data.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `solar_system_id` |
| `universe_constellation_id` | BigInt FK | → `universe_constellations.id` |
| `name` | Text | |
| `security_class` | Text | e.g. `A`, `B` |
| `security_status` | Float | ≥0.5 highsec, 0–0.5 lowsec, ≤0 nullsec |
| `stargates` | JSON | Adjacency list used by the BFS router (`evebs/engine/routing.py`) |
| `trade_hub` | Boolean | Partial index for fast hub lookup |
| `kill_stats_current_month` | Integer | Danger indicator |
| `kill_stats_last_month` | Integer | |
| `cost_indices` | JSON | Array of `{activity, cost_index}` from `/industry/systems/`; populated by `esi/update_universe_solar_system_costs.py` |

**Relationships:** `universe_constellation`, `universe_stations`, `structures`, `market_orders`

---

### `UniverseStation` — `universe_stations`
An NPC station (not a player structure). Used as an asset location and as the user's inferred current position.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `station_id` |
| `universe_system_id` | BigInt FK | → `universe_systems.id` |
| `owner_id` | BigInt | NPC corporation |
| `name` | String | |
| `office_rental_cost` | Float | |
| `reprocessing_efficiency` | Float | |
| `reprocessing_stations_take` | Float | |
| `services` | String[] | PostgreSQL array |
| `security_status` | Float | |
| `jita_distance` | Integer | Pre-computed jump distance from Jita |

**Relationships:** `universe_system`

---

### `IndustryFacility` — `industry_facilities`
An industry-capable location sourced from ESI `/industry/facilities/`. Covers both NPC stations and player-owned Upwell structures. Refreshed via `esi/update_industry_facilities.py` (full replace strategy).

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `facility_id`; no autoincrement |
| `universe_system_id` | BigInt FK | → `universe_systems.id` |
| `universe_station_id` | BigInt FK | → `universe_stations.id`; null for player structures |
| `owner_id` | BigInt | Owning corporation |
| `type_id` | BigInt | Structure type (e.g. Sotiyo, Azbel) |
| `tax` | Float | Manufacturing/research tax rate; nullable |

**Relationships:** `universe_system`, `universe_station`

---

### `UniverseCategory` — `universe_categories`
Top level of the item taxonomy (e.g. *Ship*, *Module*, *Commodity*).

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `category_id` |
| `name` | Text | |
| `published` | Boolean | |

**Relationships:** `universe_groups`

---

### `UniverseGroup` — `universe_groups`
One level below category. Groups related item types together.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `group_id` |
| `category_id` | BigInt FK | → `universe_categories.id` |
| `name` | Text | |
| `published` | Boolean | |

**Relationships:** `universe_category`, `universe_types`

---

### `UniverseType` — `universe_types`
A single in-game item type (the leaf of the item hierarchy). Referenced by almost every other model.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `type_id` |
| `group_id` | BigInt FK | → `universe_groups.id` |
| `market_group_id` | BigInt FK | → `market_groups.id` (nullable) |
| `name` | Text | |
| `description` | Text | |
| `volume` | Float | m³ per unit; used for station-score heuristic |
| `packaged_volume` | Float | m³ when packaged |
| `mass` | Float | |
| `portion_size` | BigInt | Units per reprocess batch |
| `published` | Boolean | |
| `capacity`, `radius`, `graphic_id`, `icon_id` | — | Physical attributes |

**Relationships:** `universe_group`, `market_group`, `market_orders`, `blueprint` (back-ref to the blueprint that produces this type)

**Methods:** `find_by_slug(slug)` — look up by numeric string ID.

---

## 2. Market

### `MarketGroup` — `market_groups`
Self-referential tree of market browser categories. Leaves directly contain `UniverseType` items.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `market_group_id` |
| `parent_group_id` | BigInt FK | self-ref; null for roots |
| `name` | Text | |
| `description` | Text | |

**Relationships:** `parent`, `children` (backref), `universe_types`

**Methods:** `roots()`, `is_leaf()`, `ancestors()` — tree traversal helpers.

---

### `MarketOrder` — `market_orders`
Live public market order fetched from ESI. Refreshed hourly. Both buy and sell orders are stored.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `order_id` |
| `type_id` | BigInt FK | → `universe_types.id` |
| `system_id` | BigInt FK | → `universe_systems.id` |
| `is_buy_order` | Boolean | |
| `price` | Float | |
| `volume_remain` | BigInt | |
| `volume_total` | BigInt | |
| `min_volume` | BigInt | |
| `range` | Text | e.g. `station`, `region`, `solarsystem` |
| `duration` | BigInt | Days |
| `issued` | DateTime | |
| `location_id` | BigInt | Raw ESI location; not FK-linked (may be a structure) |
| `source` | Enum | `list_order_in_a_region` or `list_order_in_a_structure` |

**Relationships:** `universe_system`, `universe_type`

---

### `MarketPrice` — `market_prices`
ESI global adjusted and average price for a type. Updated daily. Used as cost proxy when no live order is available.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | |
| `type_id` | BigInt FK | → `universe_types.id` (unique index) |
| `adjusted_price` | Float | Used as manufacturing cost input |
| `average_price` | Float | |

---

### `PublicTradeOrder` — `public_trade_orders`
Cached subset of `MarketOrder` scoped to known trade hubs. Refreshed hourly alongside `PricesMin` and `BuyOrdersAnalytic`.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | |
| `trade_hub_id` | BigInt FK | → `trade_hubs.id` |
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `order_id` | BigInt | unique |
| `is_buy_order` | Boolean | |
| `price` | Float | |
| `volume_remain` | BigInt | |
| `volume_total` | BigInt | |
| `min_volume` | BigInt | |
| `range` | String | |
| `end_time` | DateTime | |
| `touched` | Boolean | Marks orders still active after last sync |

---

### `TradeHub` — `trade_hubs`
A major market location (e.g. Jita, Amarr). Users select which hubs to watch; price pipeline runs per hub.

| Column | Type | Notes |
|---|---|---|
| `id` | Int PK | |
| `eve_system_id` | Int | unique; ESI solar system ID |
| `name` | String | |
| `region_id` | BigInt FK | → `universe_regions.id` |
| `inner` | Boolean | Internal flag for hub classification |

**Relationships:** `users` (M2M via `trade_hubs_users`), `prices_mins`, `prices_advices`, `public_trade_orders`, `buy_orders_analytics`, `production_lists`, `user_sale_orders`, `sales_finals`, `weekly_price_details`

---

## 3. Pricing & analytics

Computed tables updated by the background pipeline (`process/hourly.py`, `process/daily.py`).

### `PricesMin` — `prices_mins`
Minimum sell price and available volume for an item at a hub. Updated hourly from `PublicTradeOrder`.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | Int FK | → `universe_types.id` |
| `trade_hub_id` | Int FK | → `trade_hubs.id` |
| `min_price` | Float | Cheapest active sell order |
| `volume` | BigInt | Total volume at that price level |

Unique constraint: `(trade_hub_id, eve_item_id)`.

---

### `PricesAdvice` — `prices_advices`
Sell-order recommendation stats for an item at a hub, combining recent history with live prices. Updated daily.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | Int FK | |
| `trade_hub_id` | Int FK | |
| `vol_month` | BigInt | 30-day volume |
| `avg_price_month` | Float | |
| `avg_price_week` | Float | |
| `immediate_montly_pcent` | Float | Volume traded daily as % of monthly total |
| `margin_percent` | Float | `(min_price - cost) / cost` |

Unique constraint: `(eve_item_id, trade_hub_id)`.

---

### `BuyOrdersAnalytic` — `buy_orders_analytics`
Buy-order margin analysis per item per hub. Feeds the buy-order advice view. Updated hourly.

| Column | Type | Notes |
|---|---|---|
| `trade_hub_id` | BigInt FK | |
| `eve_item_id` | BigInt FK | |
| `approx_max_price` | Float | Estimated max price to place a buy order at |
| `over_approx_max_price_volume` | BigInt | Competing volume above max price |
| `single_unit_cost` | Float | |
| `single_unit_margin` | Float | |
| `estimated_volume_margin` | Float | |
| `per_job_margin` | Float | |
| `per_job_run_margin` | Float | |
| `final_margin` | Float | Bottom-line margin after all factors |

Unique constraint: `(trade_hub_id, eve_item_id)`.

---

### `WeeklyPriceDetail` — `weekly_price_details`
Daily volume-weighted average price for an item at a hub. Provides the 7-day rolling window used by `PricesAdvice`. Updated daily.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | BigInt FK | |
| `trade_hub_id` | BigInt FK | |
| `day` | Date | |
| `volume` | Float | |
| `weighted_avg_price` | Float | |

Unique constraint: `(eve_item_id, trade_hub_id, day)`.

---

### `EveMarketHistoriesGroup` — `eve_market_histories_groups`
Aggregated 30-day market history stats for an item in a region (not hub-specific). Used to compare regional liquidity.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | BigInt FK | |
| `universe_region_id` | BigInt FK | |
| `volume` | BigInt | 30-day total |
| `highest` | Float | |
| `lowest` | Float | |
| `average` | Float | |

---

## 4. Production

### `Blueprint` — `blueprints`
A manufacturing blueprint. Maps a produced item to its recipe. PK is the EVE blueprint type ID.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | EVE blueprint type ID (natural key, no autoincrement) |
| `produced_type_id` | BigInt FK | → `universe_types.id`; unique (one winner per item) |
| `name` | String | Copied from produced type name |
| `prod_qtt` | Int | Units produced per run |
| `nb_runs` | Int | Default run count |

**Relationships:** `blueprint_materials` (cascade delete), `blueprint_modifications`, `universe_type`

**Property:** `batch_elements_count` → `prod_qtt × nb_runs`

---

### `BlueprintMaterial` — `blueprint_materials`
One input material required by a blueprint, with quantity per run.

| Column | Type | Notes |
|---|---|---|
| `blueprint_id` | BigInt FK | → `blueprints.id` |
| `universe_type_id` | BigInt FK | → `universe_types.id` |
| `required_qtt` | BigInt | Units needed per run |

**Relationships:** `blueprint`, `universe_type`

---

### `BlueprintModification` — `blueprint_modifications`
Per-user percentage adjustment applied to a blueprint's cost calculation (e.g. material efficiency bonuses).

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `blueprint_id` | BigInt FK | |
| `percent_modification_value` | Float | Multiplier applied to material cost |
| `touched` | Boolean | Sync flag |

---

### `ProductionList` — `production_lists`
An item the user intends to manufacture, with a target run count and destination hub.

| Column | Type | Notes |
|---|---|---|
| `user_id` | Int FK | |
| `trade_hub_id` | Int FK | Target selling hub |
| `eve_item_id` | Int FK | |
| `runs_count` | Int | |

---

## 5. User & assets

### `User` — `users`
An authenticated Eve Online character (via SSO). Holds all personal preferences and download state.

| Column | Type | Notes |
|---|---|---|
| `id` | Int PK | |
| `name` | String | Character name |
| `uid` | String | EVE character ID; used in ESI endpoint paths |
| `token` | String | OAuth access token |
| `renew_token` | String | OAuth refresh token |
| `expires_on` | DateTime | Token expiry |
| `provider` | String | Always `eve` |
| `admin` | Boolean | |
| `locked` | Boolean | Prevents login if set |
| `min_pcent_for_advice` | Int | Minimum margin % to show a price advice |
| `min_amount_for_advice` | Int | Minimum ISK margin to show advice |
| `vol_month_pcent` | Int | % of monthly volume to use as batch cap |
| `batch_cap` | Boolean | Enable/disable batch size capping |
| `batch_cap_multiplier` | Int | Multiplier applied to batch cap |
| `avoid_low_sec` | Boolean | Routing preference |
| `avoid_null_sec` | Boolean | Routing preference |
| `max_jumps` | Int | Max jump radius for nearby market queries (default 5) |
| `selected_assets_station_id` | BigInt FK | User-selected station for asset view |
| `user_location_station_id` | BigInt FK | Current station fetched from ESI `/characters/{uid}/location/` |
| `download_assets_running` | Boolean | Lock flag for asset download |
| `last_assets_download` | DateTime | |
| `download_orders_running` | Boolean | |
| `last_orders_download` | DateTime | |
| `download_blueprints_running` | Boolean | |
| `last_blueprints_download` | DateTime | |
| `initialization_finalized` | Boolean | Onboarding complete flag |

**Relationships:** `trade_hubs` (M2M), `eve_items` (M2M watchlist), `production_lists`, `user_sale_orders`, `bpc_assets`, `bpc_assets_stations`, `blueprint_modifications`, `eve_items_saved_lists`, `user_location_station`

**Properties:** `eve_item_ids`, `trade_hub_ids`

---

### `BpcAsset` — `bpc_assets`
A single item stack in the user's in-game asset inventory, as downloaded from ESI `/characters/{uid}/assets/`.

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `universe_station_id` | BigInt FK | Nullable; null if in a structure or space |
| `quantity` | BigInt | |
| `touched` | Boolean | Cleared before sync; rows with `touched=False` after sync are stale |

**Relationships:** `user`, `universe_type`, `universe_station`

---

### `BpcAssetsStation` — `bpc_assets_stations`
Stations the user has explicitly registered as BPC storage locations. Used to scope the asset sync.

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `universe_station_id` | BigInt FK | |
| `touched` | Boolean | Sync flag |

---

### `UserSaleOrder` — `user_sale_orders`
A sell order the user has placed on the market. Tracked for margin reporting.

| Column | Type | Notes |
|---|---|---|
| `user_id` | Int FK | |
| `eve_item_id` | Int FK | |
| `trade_hub_id` | Int FK | |
| `price` | Float | Placed sell price |

---

### `SalesFinal` — `sales_finals`
Completed sale event detected when a sell order's remaining volume decreases or the order expires. Written by the daily process.

| Column | Type | Notes |
|---|---|---|
| `day` | Date | Date of the sale |
| `trade_hub_id` | BigInt FK | |
| `eve_item_id` | BigInt FK | |
| `order_id` | BigInt | Original order ID |
| `volume` | BigInt | Units sold |
| `price` | Float | Sale price |

---

### `EveItemsSavedList` — `eve_items_saved_lists`
Named snapshot of the user's item watchlist, stored as a JSON array of type IDs.

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `description` | String | User-provided label |
| `saved_ids` | Text | JSON-serialised `[type_id, ...]` |

**Methods:** `get_ids()`, `set_ids(ids)`

---

## 6. Infrastructure

### `Constant` — `constants`
Named numeric constant used in price formulas (e.g. `taxes = 1.13`).

| Column | Type | Notes |
|---|---|---|
| `libe` | String | Unique key (e.g. `"taxes"`) |
| `f_value` | Float | The value |
| `description` | String | |

---

### `Crontab` — `crontabs`
Mutex guard preventing concurrent cron job runs. Each named process has one row; `status=True` means it is running.

| Column | Type | Notes |
|---|---|---|
| `cron_name` | String | Process identifier |
| `status` | Boolean | `True` = running |

**Methods:** `start(cron_name)` — acquire lock or exit; `stop(cron_name)` — release. Both are no-ops in development.

---

### `LastUpdate` — `last_updates`
Records the timestamp of the last successful run for each background process type.

| Column | Type | Notes |
|---|---|---|
| `update_type` | String | e.g. `"hourly"`, `"daily"` |
| `updated_at` | DateTime | |

**Methods:** `set(update_type)` — upsert.

---

### `Structure` — `structures`
A player-built structure (citadel, refinery). Tracked for market data fetching. Most structures are `forbidden=True` (access denied by default).

| Column | Type | Notes |
|---|---|---|
| `cpp_structure_id` | BigInt | EVE structure ID (unique) |
| `forbidden` | Boolean | Default `True`; set `False` to include in order sync |
| `universe_system_id` | BigInt FK | Nullable |
| `orders_count_pages` | Int | Cached pagination hint for order downloads |

---

### `UserActivityLog` — `user_activity_logs`
Audit log for admin review. Records IP, action string, and character name.

| Column | Type | Notes |
|---|---|---|
| `ip` | String | |
| `action` | String | |
| `user` | String | Character name at time of action |

---

### `UserToUserDuplicationRequest` — `user_to_user_duplication_requests`
Request to copy one user's settings or watchlist to another user (admin feature).

| Column | Type | Notes |
|---|---|---|
| `sender_id` | Int FK | |
| `receiver_id` | Int FK | |
| `duplication_type` | Int | Enum-style discriminator |

---

## 7. SQL views (read-only)

These models map to SQL views created at startup in `evebs/__init__.py:_create_views()`. They are **never migrated** — the view is dropped and recreated on every app start. Marked with `__table_args__ = {'info': {'is_view': True}}`.

| Model | View table | Purpose |
|---|---|---|
| `BuyOrdersAnalyticsResult` | `buy_orders_analytics_results` | Joins buy-order analytics with user settings and item names for the buy-advice screen |
| `PriceAdvicesMinPrice` | `price_advices_min_prices` | Combines `PricesAdvice` with current min prices and item cost for the sell-advice screen |
| `UserSaleOrderDetail` | `user_sale_order_details` | Enriches user sell orders with item name, min price, and price delta |
| `PriceAdviceMarginComp` | `price_advice_margin_comps` | Full margin comparison per item/hub filtered by user thresholds |
| `ComponentToBuy` | `components_to_buys` | Lists materials the user still needs to purchase for their production list |

---

## 8. Association tables

Plain join tables with no dedicated model class.

| Table | Joins | Purpose |
|---|---|---|
| `eve_items_users` | `users` ↔ `universe_types` | User's item watchlist (M2M) |
| `trade_hubs_users` | `users` ↔ `trade_hubs` | Hubs a user is monitoring (M2M) |
