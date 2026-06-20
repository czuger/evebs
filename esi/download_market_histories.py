import argparse
import os
import sys
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from config import set_logger
from esi.client import EsiClient
from esi.errors import BadRequest, EsiError, NotFound
from evebs import create_db_app
from evebs.extensions import db
from evebs.models import UniverseRegion, MarketHistory

# Dedicated, isolated debug log — logs/download_market_histories.log (does not propagate
# to the console or evebs.log).
logger = set_logger('download_market_histories')

FORGE_REGION_ID = 10000002   # The Forge (Jita) — same id reference_data.py uses
_INSERT_CHUNK = 1000


def _insert(rows, session=None):
    """Insert MarketHistory rows, skipping any (region_id, type_id, date) already
    stored. Dialect-aware (Postgres prod / SQLite dev); chunked for the bind-param limit.
    """
    session = session or db.session
    if not rows:
        return
    ins = pg_insert if session.get_bind().dialect.name == 'postgresql' else sqlite_insert
    for i in range(0, len(rows), _INSERT_CHUNK):
        stmt = ins(MarketHistory).on_conflict_do_nothing(
            index_elements=['region_id', 'type_id', 'date'])
        session.execute(stmt, rows[i:i + _INSERT_CHUNK])


def download_market_histories(forge_only=False, session=None):
    """Download exact daily market history per region/type from ESI and insert it
    verbatim into market_histories. /types enumerates the type_ids per region;
    /history is then fetched per type and each daily record is stored as-is.

    forge_only=True restricts to The Forge. Returns {'regions', 'records'}.
    """
    session = session or db.session
    regions = session.query(UniverseRegion).all()
    if forge_only:
        regions = [r for r in regions if r.id == FORGE_REGION_ID]

    logger.info('[market_history] starting — %s region(s)%s',
                len(regions), ' (forge only)' if forge_only else '')

    run_start = time.perf_counter()
    esi_types_s = esi_history_s = db_s = 0.0

    total = 0
    for region_idx, region in enumerate(regions, 1):
        region_start = time.perf_counter()
        logger.info('[market_history] [%s/%s] region %s (id %s) — fetching type list',
                    region_idx, len(regions), region.name, region.id)
        try:
            t0 = time.perf_counter()
            type_ids = EsiClient(f'markets/{region.id}/types/').get_all_pages()
            esi_types_s += time.perf_counter() - t0
        except EsiError as e:
            logger.warning('[market_history] [%s/%s] region %s (id %s) — ERROR fetching types: %s',
                           region_idx, len(regions), region.name, region.id, e)
            continue

        logger.info('[market_history] [%s/%s] region %s (id %s) — %s types to download',
                    region_idx, len(regions), region.name, region.id, len(type_ids))

        region_records = 0
        for type_idx, type_id in enumerate(type_ids, 1):
            logger.debug('[market_history] region %s (id %s) — downloading history for type %s (%s/%s)',
                         region.name, region.id, type_id, type_idx, len(type_ids))
            try:
                t0 = time.perf_counter()
                records = EsiClient(f'markets/{region.id}/history/',
                                    params={'type_id': type_id}).get_all_pages()
                esi_history_s += time.perf_counter() - t0
            except (NotFound, BadRequest):
                logger.debug('[market_history] region %s (id %s) — type %s has no history, skipping',
                             region.name, region.id, type_id)
                continue

            rows = []
            for rec in records:
                try:
                    day = date.fromisoformat(rec['date'])
                except (KeyError, ValueError, TypeError):
                    continue
                rows.append({
                    'region_id':   region.id,
                    'type_id':     type_id,
                    'date':        day,
                    'average':     rec.get('average'),
                    'highest':     rec.get('highest'),
                    'lowest':      rec.get('lowest'),
                    'order_count': rec.get('order_count'),
                    'volume':      rec.get('volume'),
                })

            t0 = time.perf_counter()
            _insert(rows, session=session)
            session.commit()
            db_s += time.perf_counter() - t0

            total += len(rows)
            region_records += len(rows)
            logger.debug('[market_history] region %s (id %s) — type %s: %s daily records',
                         region.name, region.id, type_id, len(rows))

            time.sleep(0.2)

        logger.info('[market_history] [%s/%s] region %s (id %s) done — %s types, %s records in %.1fs',
                    region_idx, len(regions), region.name, region.id, len(type_ids), region_records,
                    time.perf_counter() - region_start)

    total_elapsed = time.perf_counter() - run_start
    other_s = total_elapsed - esi_types_s - esi_history_s - db_s
    logger.info('[market_history] finished — %s regions, %s records in %.1fs',
                len(regions), total, total_elapsed)
    logger.info('[market_history] timing summary — total %.1fs | ESI /types %.1fs | ESI /history %.1fs | '
                'DB insert+commit %.1fs | other %.1fs | %.0f records/s',
                total_elapsed, esi_types_s, esi_history_s, db_s, other_s,
                total / total_elapsed if total_elapsed else 0)
    return {
        'regions': len(regions), 'records': total, 'elapsed': total_elapsed,
        'esi_types_s': esi_types_s, 'esi_history_s': esi_history_s, 'db_s': db_s,
    }


def main():
    # No setup_logging() / full app: this script logs only to its own
    # logs/download_market_histories.log (set_logger above) and runs against a DB-only
    # app, so it never imports blueprints or opens logs/timings.log. See CLAUDE.md.
    parser = argparse.ArgumentParser(
        description='Download exact per-region market history from ESI into market_histories.')
    parser.add_argument('-f', '--forge', action='store_true',
                        help='Download The Forge (Jita) region only.')
    args = parser.parse_args()

    with create_db_app().app_context():
        download_market_histories(forge_only=args.forge)


if __name__ == '__main__':
    main()
