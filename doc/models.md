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
7. [Materialized-view models](#7-materialized-view-models)
8. [SQL view models (parked)](#8-sql-view-models-parked)
9. [Association tables](#9-association-tables)

---

## 1. Universe hierarchy

Static data imported from the ESI API. Reflects the in-game geographic and item taxonomy. Updated infrequently (weekly process).

### `UniverseRegion` — `universe_regions`
Top-level geographic unit. Contains constellations.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `region_id` |
| `name` | Text | |
| `description` | Text | |

**Relationships:** `universe_constellations`, `eve_market_histories_groups`

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
A solar system. Central hub for routing, market orders, industry cost data, and trade hub selection.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `solar_system_id` |
| `universe_constellation_id` | BigInt FK | → `universe_constellations.id` |
| `name` | Text | |
| `security_class` | Text | e.g. `A`, `B` |
| `security_status` | Float | ≥0.5 highsec, 0–0.5 lowsec, ≤0 nullsec |
| `stargates` | JSON | Adjacency list used by the BFS router (`evebs/engine/routing.py`) |
| `trade_hub` | Boolean | Partial index; set by `esi/update_universe_set_trade_hub.py` on top-volume highsec systems |
| `kill_stats_current_month` | Integer | Danger indicator |
| `kill_stats_last_month` | Integer | |
| `cost_indices` | JSON | Array of `{activity, cost_index}` from `/industry/systems/` |

**Relationships:** `universe_constellation`, `universe_stations`, `structures`, `market_orders`

**Property:** `universe_region` — traverses `universe_constellation → universe_region`; used in templates to avoid a three-level chain.

---

### `UniverseStation` — `universe_stations`
An NPC station. Used as an asset location and as the user's inferred current position.

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
An industry-capable location from ESI `/industry/facilities/`. Covers NPC stations and Upwell structures. Full-replace on each refresh.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `facility_id`; no autoincrement |
| `universe_system_id` | BigInt FK | → `universe_systems.id` |
| `universe_station_id` | BigInt FK | → `universe_stations.id`; null for player structures |
| `owner_id` | BigInt | |
| `type_id` | BigInt | Structure type |
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
One level below category. Groups related item types.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `group_id` |
| `category_id` | BigInt FK | → `universe_categories.id` |
| `name` | Text | |
| `published` | Boolean | |

**Relationships:** `universe_category`, `universe_types`

---

### `UniverseType` — `universe_types`
A single in-game item type (leaf of the item hierarchy). Referenced by almost every other model.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | ESI `type_id` |
| `group_id` | BigInt FK | → `universe_groups.id` |
| `market_group_id` | BigInt FK | → `market_groups.id` (nullable) |
| `name` | Text | |
| `description` | Text | |
| `volume` | Float | m³ per unit |
| `packaged_volume` | Float | m³ when packaged |
| `mass` | Float | |
| `portion_size` | BigInt | Units per reprocess batch |
| `published` | Boolean | |
| `cost` | Float | Manufacturing cost per unit; computed by the daily pipeline |
| `weekly_avg_price` | Float | Volume-weighted 7-day average from Jita sales; updated daily |
| `base_item` | Boolean | `True` if this type has no blueprint (raw material) |
| `capacity`, `radius`, `graphic_id`, `icon_id` | — | Physical attributes |

**Relationships:** `universe_group`, `market_group`, `market_orders`, `blueprint` (viewonly back-ref to the blueprint that produces this type)

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
Live public market order fetched from ESI. Refreshed hourly. Both buy and sell orders stored.

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
ESI global adjusted and average price for a type. Updated daily.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | |
| `type_id` | BigInt FK | → `universe_types.id` (unique index) |
| `adjusted_price` | Float | Used as manufacturing cost input |
| `average_price` | Float | |

---

## 3. Pricing & analytics

Computed tables updated by the background pipeline (`process/hourly.py`, `process/daily.py`).

### `PricesAdvice` — `prices_advices`
Sell-order recommendation stats for an item at a system, combining recent history with live prices. Updated daily.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | Int FK | → `universe_types.id` |
| `system_id` | Int FK | → `universe_systems.id` |
| `vol_month` | BigInt | 30-day volume |
| `avg_price_month` | Float | |
| `avg_price_week` | Float | |
| `immediate_montly_pcent` | Float | Volume traded daily as % of monthly total |
| `margin_percent` | Float | `(p10_price - cost) / cost` |

Unique constraint: `(eve_item_id, system_id)`.

**Relationships:** `eve_item`, `universe_system`

---

### `BuyOrdersAnalytic` — `buy_orders_analytics`
Buy-order margin analysis per item per system. Updated hourly.

| Column | Type | Notes |
|---|---|---|
| `system_id` | BigInt FK | → `universe_systems.id` |
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `approx_max_price` | Float | 90% of highest buy order |
| `over_approx_max_price_volume` | BigInt | Competing buy volume above that price |
| `single_unit_cost` | Float | |
| `single_unit_margin` | Float | |
| `estimated_volume_margin` | Float | |
| `final_margin` | Float | Capped by blueprint batch size |

Unique constraint: `(system_id, eve_item_id)`.

**Relationships:** `universe_system`, `eve_item`

---

### `WeeklyPriceDetail` — `weekly_price_details`
Daily volume-weighted average price for an item at a system. Provides the 7-day rolling window used by `PricesAdvice`. Updated daily.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `system_id` | BigInt FK | → `universe_systems.id` |
| `day` | Date | |
| `volume` | Float | |
| `weighted_avg_price` | Float | |

Unique constraint: `(eve_item_id, system_id, day)`.

**Relationships:** `universe_system`, `eve_item`

---

### `EveMarketHistoriesGroup` — `eve_market_histories_groups`
Aggregated 30-day market history stats for an item in a region (not system-specific). Used to compare regional liquidity.

| Column | Type | Notes |
|---|---|---|
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `universe_region_id` | BigInt FK | → `universe_regions.id` |
| `volume` | BigInt | 30-day total |
| `highest` | Float | |
| `lowest` | Float | |
| `average` | Float | |

---

### `IndustryInterestingItem` — `industry_interesting_items`
A (region, item) pair the user has flagged for targeted market download.

| Column | Type | Notes |
|---|---|---|
| `region_id` | BigInt FK | → `universe_regions.id` |
| `item_id` | BigInt FK | → `universe_types.id` |

Unique constraint: `(region_id, item_id)`.

**Relationships:** `universe_region`, `universe_type`

---

## 4. Production

### `Blueprint` — `blueprints`
A manufacturing blueprint. Maps a produced item to its recipe.

| Column | Type | Notes |
|---|---|---|
| `id` | BigInt PK | EVE blueprint type ID (natural key, no autoincrement) |
| `produced_type_id` | BigInt FK | → `universe_types.id`; unique |
| `name` | String | Copied from produced type name |
| `prod_qtt` | Int | Units produced per run |
| `nb_runs` | Int | Default run count |

**Relationships:** `blueprint_materials` (cascade delete), `blueprint_modifications`, `universe_type`

**Property:** `batch_elements_count` → `prod_qtt × nb_runs`

---

### `BlueprintMaterial` — `blueprint_materials`
One input material required by a blueprint.

| Column | Type | Notes |
|---|---|---|
| `blueprint_id` | BigInt FK | → `blueprints.id` |
| `universe_type_id` | BigInt FK | → `universe_types.id` |
| `required_qtt` | BigInt | Units needed per run |

**Relationships:** `blueprint`, `universe_type`

---

### `BlueprintModification` — `blueprint_modifications`
Per-user percentage adjustment applied to a blueprint's material cost (e.g. material efficiency bonuses).

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `blueprint_id` | BigInt FK | |
| `percent_modification_value` | Float | Multiplier applied to material cost |
| `touched` | Boolean | Sync flag |

---

### `ProductionList` — `production_lists`
An item the user intends to manufacture, with a target run count and destination system.

| Column | Type | Notes |
|---|---|---|
| `user_id` | Int FK | → `users.id` |
| `system_id` | Int FK | → `universe_systems.id` |
| `eve_item_id` | Int FK | → `universe_types.id` |
| `runs_count` | Int | |

**Relationships:** `user`, `universe_system`, `eve_item`

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
| `provider` | String | Always `eve_online_sso` |
| `admin` | Boolean | |
| `locked` | Boolean | Prevents background downloads if set |
| `min_pcent_for_advice` | Int | Minimum margin % to show a price advice |
| `min_amount_for_advice` | Int | Minimum ISK margin to show advice |
| `vol_month_pcent` | Int | % of monthly volume to use as batch cap |
| `batch_cap` | Boolean | Enable/disable batch size capping |
| `batch_cap_multiplier` | Int | Multiplier applied to batch cap |
| `facility_tax` | Float | Manufacturing facility tax (%) |
| `scc_surcharge` | Float | SCC surcharge (%) |
| `avoid_low_sec` | Boolean | Routing preference |
| `avoid_null_sec` | Boolean | Routing preference |
| `max_jumps` | Int | Max jump radius for nearby market queries (default 5) |
| `selected_assets_station_id` | BigInt FK | → `universe_stations.id` |
| `user_location_station_id` | BigInt FK | → `universe_stations.id` |
| `initialization_finalized` | Boolean | Onboarding complete flag |

**Relationships:** `universe_systems` (M2M watchlist of trade hubs), `eve_items` (M2M item watchlist), `production_lists`, `user_sale_orders`, `bpc_assets`, `bpc_assets_stations`, `blueprint_modifications`, `eve_items_saved_lists`, `user_location_station`

**Properties:** `eve_item_ids`, `trade_hub_ids` (returns IDs of watched `universe_systems`)

---

### `BpcAsset` — `bpc_assets`
A single item stack in the user's in-game asset inventory, from ESI `/characters/{uid}/assets/`.

| Column | Type | Notes |
|---|---|---|
| `user_id` | BigInt FK | |
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `universe_station_id` | BigInt FK | Nullable; null if in a structure or space |
| `quantity` | BigInt | |
| `touched` | Boolean | Cleared before sync; stale rows have `touched=False` after sync |

**Relationships:** `user`, `universe_type`, `universe_station`

---

### `BpcAssetsStation` — `bpc_assets_stations`
Stations the user has registered as BPC storage locations. Scopes the asset sync.

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
| `eve_item_id` | Int FK | → `universe_types.id` |
| `system_id` | Int FK | → `universe_systems.id` |
| `price` | Float | Placed sell price |

**Relationships:** `user`, `eve_item`, `universe_system`

---

### `SalesFinal` — `sales_finals`
Completed sale event detected when a sell order's volume decreases or the order expires. Written by the daily process.

| Column | Type | Notes |
|---|---|---|
| `day` | Date | Date of the sale |
| `system_id` | BigInt FK | → `universe_systems.id` |
| `eve_item_id` | BigInt FK | → `universe_types.id` |
| `order_id` | BigInt | Original order ID |
| `volume` | BigInt | Units sold |
| `price` | Float | Sale price |

**Relationships:** `universe_system`, `eve_item`

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
| `libe` | String | Unique key |
| `f_value` | Float | The value |
| `description` | String | |

---

### `Crontab` — `crontabs`
Mutex guard preventing concurrent cron job runs.

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
A player-built structure (citadel, refinery). Tracked for market data fetching. Most are `forbidden=True` by default.

| Column | Type | Notes |
|---|---|---|
| `cpp_structure_id` | BigInt | EVE structure ID (unique) |
| `forbidden` | Boolean | Default `True`; set `False` to include in order sync |
| `universe_system_id` | BigInt FK | Nullable |
| `orders_count_pages` | Int | Cached pagination hint |

---

### `UserActivityLog` — `user_activity_logs`
Audit log for admin review.

| Column | Type | Notes |
|---|---|---|
| `ip` | String | |
| `action` | String | |
| `user` | String | Character name at time of action |

---

### `UserToUserDuplicationRequest` — `user_to_user_duplication_requests`
Request to copy one user's settings or watchlist to another (admin feature).

| Column | Type | Notes |
|---|---|---|
| `sender_id` | Int FK | |
| `receiver_id` | Int FK | |
| `duplication_type` | Int | Enum-style discriminator |

---

## 7. Materialized-view models

These models map to PostgreSQL **materialized views** created in migration `0017`. Refreshed concurrently by the hourly process. Marked with `__table_args__ = {'info': {'is_view': True}}` — never migrate them directly.

### `MarketSellerPrice` — `market_seller_prices`
Volume-weighted p10 sell price per `(type_id, system_id)`. Built from `market_orders WHERE is_buy_order = FALSE`.

| Column | Type | Notes |
|---|---|---|
| `type_id` | BigInt PK | → `universe_types.id` |
| `system_id` | BigInt PK | → `universe_systems.id` |
| `p10_price` | Float | Price at which cumulative volume ≥ 5% of total |
| `volume` | BigInt | Total sell volume in that system |

**Relationships:** `universe_type`, `universe_system`

---

### `MarketBuyerPrice` — `market_buyer_prices`
Volume-weighted p90 buy price per `(type_id, system_id)`. Built from `market_orders WHERE is_buy_order = TRUE`.

| Column | Type | Notes |
|---|---|---|
| `type_id` | BigInt PK | → `universe_types.id` |
| `system_id` | BigInt PK | → `universe_systems.id` |
| `p90_price` | Float | Price at which cumulative volume ≥ 10% of total (desc) |
| `volume` | BigInt | Total buy volume |

**Relationships:** `universe_type`, `universe_system`

---

## 8. SQL view models (parked)

These models in `evebs/models/views.py` map to SQL views whose definitions are parked in `oldies/sql/sql_views.py` pending rework. The views are **not currently created** — do not query these models until the views are reinstated.

| Model | View table | Purpose |
|---|---|---|
| `BuyOrdersAnalyticsResult` | `buy_orders_analytics_results` | Buy-order analytics joined with user settings and item names |
| `PriceAdvicesMinPrice` | `price_advices_min_prices` | `PricesAdvice` joined with current min price and item cost |
| `UserSaleOrderDetail` | `user_sale_order_details` | User sell orders enriched with item name and price delta |
| `PriceAdviceMarginComp` | `price_advice_margin_comps` | Full margin comparison per item/system filtered by user thresholds |
| `ComponentToBuy` | `components_to_buys` | Materials the user still needs to purchase for their production list |

---

## 9. Association tables

Plain join tables with no dedicated model class.

| Table | Joins | Purpose |
|---|---|---|
| `eve_items_users` | `users` ↔ `universe_types` | User's item watchlist (M2M) |
| `universe_systems_users` | `users` ↔ `universe_systems` | Trade hub systems a user is monitoring (M2M) |
