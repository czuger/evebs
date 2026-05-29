#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import setup_logging
setup_logging()

from esi.client import EsiClient
from esi.errors import NotFound
from esi.download_history import _ammo_market_group_ids
from evebs.extensions import db
from evebs.models import (
    TradeHub, EveItem, UniverseRegion,
    PublicTradeOrder, SalesFinal,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


class DownloadPublicTradesOrders:
    # EVE Online cpp_region_id for The Forge (contains Jita 4-4)
    FORGE_REGION_ID = 10000002

    def __init__(self, essentials: bool = False, forge_only: bool = False) -> None:
        """Initialise the downloader.

        Args:
            essentials:  When True, restrict the download to trade-hub regions
                         and ammunition/charges item types only. Useful for a
                         fast hourly refresh that avoids downloading the full
                         universe of market data.
            forge_only:  When True, download only The Forge region (cpp_region_id=10000002, Jita).
                         Takes precedence over ``essentials`` for region filtering.
        """
        self.essentials = essentials
        self.forge_only = forge_only

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_reference_data(self) -> tuple[dict[int, int], dict[int, int], list]:
        """Load hub, item, and region reference data from the database.

        Builds two lookup dicts keyed by EVE Online IDs so that order rows
        can be resolved to internal DB PKs in O(1) during the upsert loop.
        When ``self.essentials`` is True, the region list is restricted to
        trade-hub regions and the item map is restricted to ammo/charges types.

        Returns:
            (hub_map, item_map, regions) where
            hub_map  = {eve_system_id: trade_hub.id},
            item_map = {cpp_eve_item_id: eve_item.id},
            regions  = list of UniverseRegion ORM objects.
        """
        hub_map  = {th.eve_system_id: th.id for th in TradeHub.query.all()}
        item_map = {ei.cpp_eve_item_id: ei.id for ei in EveItem.query.all()}
        regions  = UniverseRegion.query.all()

        if self.forge_only:
            regions = [r for r in regions if r.cpp_region_id == self.FORGE_REGION_ID]
            logger.info('[orders] forge-only mode: region %d', self.FORGE_REGION_ID)

        elif self.essentials:
            hub_cpp_ids    = {int(th.region.cpp_region_id) for th in TradeHub.query.all() if th.region}
            regions        = [r for r in regions if r.cpp_region_id in hub_cpp_ids]
            ammo_group_ids = _ammo_market_group_ids()
            ammo_cpp_ids   = {
                item.cpp_eve_item_id
                for item in EveItem.query.filter(EveItem.market_group_id.in_(ammo_group_ids)).all()
            }
            item_map = {k: v for k, v in item_map.items() if k in ammo_cpp_ids}
            logger.info('[orders] essentials mode: %d hub regions, %d ammo/charges types',
                        len(regions), len(item_map))

        return hub_map, item_map, regions

    def _fetch_region_types(self, region) -> set[int]:
        """Fetch all typeIDs that have active orders in a region from ESI.

        Used to pre-filter the download to only item types we track, avoiding
        downloading orders for the thousands of types we have no interest in.
        Retries once on a transient ``NotFound`` response.

        Args:
            region: A UniverseRegion ORM object with a ``cpp_region_id`` field.

        Returns:
            Set of integer typeIDs with at least one active order in the region.
        """
        client = EsiClient(f'markets/{region.cpp_region_id}/types/')
        try:
            type_ids = client.get_all_pages()
        except NotFound:
            logger.warning('NotFound for region %s types — retrying in 60s', region.name)
            time.sleep(60)
            type_ids = client.get_all_pages()
        return set(type_ids)

    def _fetch_type_orders(self, region, type_id: int) -> list[dict]:
        """Fetch all orders for a single item type in a region from ESI.

        Filtering by ``type_id`` at the ESI level means only relevant orders
        are transferred. Pagination is handled transparently by the client.
        Retries once on a transient ``NotFound`` response.

        Args:
            region:  A UniverseRegion ORM object with a ``cpp_region_id`` field.
            type_id: EVE Online typeID to filter orders by.

        Returns:
            List of raw ESI order dicts for that item type in that region.
        """
        client = EsiClient(f'markets/{region.cpp_region_id}/orders/', params={'type_id': type_id})
        try:
            return client.get_all_pages()
        except NotFound:
            logger.warning('NotFound for region %s type %d — retrying in 60s', region.name, type_id)
            time.sleep(60)
            return client.get_all_pages()

    def _upsert_order(
        self,
        order_data: dict,
        hub_id: int,
        item_id: int,
        existing: dict,
    ) -> tuple[str, int]:
        """Insert or update a single public trade order in the database session.

        For existing orders, only ``volume_remain``, ``price``, and ``end_time``
        are updated. When a sell order's remaining volume has decreased a
        ``SalesFinal`` record is added to the session to track the implied sale.
        New orders are added to both the DB session and the ``existing`` dict so
        that subsequent iterations of the same order_id are handled as updates.

        Args:
            order_data: Raw ESI order dict (keys: order_id, price, volume_remain,
                        is_buy_order, issued, duration, range, volume_total, min_volume).
            hub_id:     Internal DB PK for the trade hub (trade_hub.id).
            item_id:    Internal DB PK for the item (eve_item.id).
            existing:   Mutable dict {order_id: PublicTradeOrder} used as the
                        local cache; updated in-place when a new order is created.

        Returns:
            (action, sales_created) where action ∈ {'created', 'updated', 'unchanged'}
            and sales_created is 0 or 1.
        """
        issued        = datetime.strptime(order_data['issued'][:19], '%Y-%m-%dT%H:%M:%S')
        end_time      = issued + timedelta(days=order_data.get('duration', 0))
        order_id      = order_data['order_id']
        volume_remain = order_data['volume_remain']
        price         = order_data['price']

        o = existing.get(order_id)
        if o:
            changed = (
                o.volume_remain != volume_remain or
                o.price != price or
                o.end_time != end_time
            )
            if changed:
                # Record a sale when a sell order's remaining volume shrank
                sales_created = 0
                if not order_data.get('is_buy_order') and o.volume_remain > volume_remain:
                    db.session.add(SalesFinal(
                        day=datetime.utcnow().date(),
                        trade_hub_id=o.trade_hub_id,
                        eve_item_id=o.eve_item_id,
                        volume=o.volume_remain - volume_remain,
                        price=price,
                        order_id=order_id,
                    ))
                    sales_created = 1
                o.volume_remain = volume_remain
                o.price         = price
                o.end_time      = end_time
                o.touched       = True
                return 'updated', sales_created
            else:
                o.touched = True
                return 'unchanged', 0
        else:
            new_order = PublicTradeOrder(
                order_id      = order_id,
                trade_hub_id  = hub_id,
                eve_item_id   = item_id,
                is_buy_order  = order_data.get('is_buy_order', False),
                end_time      = end_time,
                price         = price,
                range         = order_data.get('range', 'station'),
                volume_remain = volume_remain,
                volume_total  = order_data.get('volume_total', volume_remain),
                min_volume    = order_data.get('min_volume', 1),
                touched       = True,
            )
            db.session.add(new_order)
            existing[order_id] = new_order
            return 'created', 0

    def _flush_expired_orders(self, now: datetime) -> int:
        """Record expired untouched sell orders as sales, then return their count.

        An order is considered expired if it is still marked ``touched=False``
        after the download loop (i.e. ESI no longer reports it) and its
        ``end_time`` is in the past. Each such order produces one ``SalesFinal``
        entry before being deleted by the bulk cleanup in ``download()``.

        Args:
            now: Current UTC datetime used as the reference for expiry checks
                 and as the sale date.

        Returns:
            Number of expired orders recorded as sales.
        """
        expired = PublicTradeOrder.query.filter(
            PublicTradeOrder.touched.is_(False),
            PublicTradeOrder.is_buy_order.is_(False),
            PublicTradeOrder.end_time < now,
        ).all()

        for old in expired:
            db.session.add(SalesFinal(
                day=now.date(),
                trade_hub_id=old.trade_hub_id,
                eve_item_id=old.eve_item_id,
                volume=old.volume_remain,
                price=old.price,
                order_id=old.order_id,
            ))

        logger.debug('%d expired orders → sales_finals', len(expired))
        return len(expired)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def download(self) -> None:
        """Download all public market orders from ESI and upsert them into the DB.

        Processing steps:
          1. Load reference lookups (hub_map, item_map, regions).
          2. Pre-load all existing PublicTradeOrder rows and mark them untouched.
          3. For each region: fetch active typeIDs from ESI, intersect with
             item_map to get relevant types, then fetch orders per type and
             upsert each order belonging to a known trade hub.
             Orders are committed to the DB every BATCH_SIZE rows.
          4. Record expired untouched sell orders as SalesFinal entries.
          5. Delete all remaining untouched orders (disappeared from ESI).
          6. Final commit and summary log.

        Counters tracked: created, updated, unchanged, deleted, sales_created,
        skipped_no_hub, skipped_zero_volume.
        Batch progress logs include per-region types/s rate and wall-clock ETA.
        """
        t0 = time.perf_counter()

        hub_map, item_map, regions = self._load_reference_data()

        # Pre-load all known orders for O(1) lookup during upsert
        existing: dict[int, PublicTradeOrder] = {
            o.order_id: o for o in PublicTradeOrder.query.all()
        }
        logger.debug('Reference data loaded: %d hubs | %d items | %d existing orders',
                     len(hub_map), len(item_map), len(existing))

        # Stamp every order as untouched; orders still untouched after the loop
        # have disappeared from ESI and will be deleted at the end.
        PublicTradeOrder.query.update({'touched': False})
        db.session.flush()

        created = updated = touched = 0
        skipped_no_hub = skipped_zero = 0
        sales_created = 0
        batch = 0
        item_map_keys = set(item_map.keys())

        for region in regions:
            region_type_ids = self._fetch_region_types(region)
            relevant_types  = region_type_ids & item_map_keys
            logger.debug('%s: %d/%d types with orders are tracked',
                         region.name, len(relevant_types), len(region_type_ids))

            total_relevant = len(relevant_types)
            region_start   = time.perf_counter()
            for types_processed, type_id in enumerate(relevant_types, 1):
                item_id = item_map[type_id]

                for order_data in self._fetch_type_orders(region, type_id):
                    hub_id = hub_map.get(order_data.get('system_id'))

                    if not hub_id:
                        skipped_no_hub += 1
                        continue
                    if order_data.get('volume_remain', 0) == 0:
                        skipped_zero += 1
                        continue

                    action, n_sales = self._upsert_order(order_data, hub_id, item_id, existing)
                    sales_created += n_sales
                    if action == 'created':
                        created += 1
                    elif action == 'updated':
                        updated += 1
                    else:
                        touched += 1

                    batch += 1
                    if batch % BATCH_SIZE == 0:
                        db.session.commit()
                        region_elapsed = time.perf_counter() - region_start
                        type_rate = types_processed / region_elapsed if region_elapsed > 0 else 0
                        eta_s     = (total_relevant - types_processed) / type_rate if type_rate > 0 else 0
                        eta_at    = datetime.now() + timedelta(seconds=eta_s)
                        logger.debug(
                            '... %d orders | types %d/%d | +%d created ~%d updated =%d unchanged'
                            ' | %.1f types/s  ETA ~%s',
                            batch, types_processed, total_relevant,
                            created, updated, touched, type_rate, eta_at.strftime('%y/%d/%m %H:%M:%S'),
                        )

        now = datetime.utcnow()
        sales_created += self._flush_expired_orders(now)

        deleted_q = PublicTradeOrder.query.filter(PublicTradeOrder.touched.is_(False))
        deleted   = deleted_q.count()
        deleted_q.delete()

        db.session.commit()

        elapsed = time.perf_counter() - t0
        logger.info(
            'Done in %.1fs — +%d created ~%d updated =%d unchanged -%d deleted | '
            '%d sales recorded | skipped: %d no-hub  %d zero-volume',
            elapsed, created, updated, touched, deleted, sales_created,
            skipped_no_hub, skipped_zero,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download public market orders from ESI and upsert into DB.')
    parser.add_argument('-e', '--essentials', action='store_true',
                        help='Restrict to trade-hub regions and ammo/charges types only.')
    parser.add_argument('-f', '--forge', action='store_true',
                        help='Download only The Forge region (Jita). Takes precedence over --essentials.')
    args = parser.parse_args()

    from app import app
    with app.app_context():
        DownloadPublicTradesOrders(essentials=args.essentials, forge_only=args.forge).download()
