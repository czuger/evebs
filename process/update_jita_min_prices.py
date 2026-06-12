#!/usr/bin/env python3
"""Refresh the jita_min_prices materialized view (P10 Jita sell price per item type).

The view computes, per item, the P10 ask at Jita (system 30000142) over
public_trade_orders. Refreshing recomputes it from the current orders.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from config import set_logger
from evebs import create_db_app
from evebs.extensions import db

logger = set_logger('update_jita_min_prices')


def update_jita_min_prices():
    # Plain (non-concurrent) refresh — see CLAUDE.md. Briefly locks the view but needs no
    # unique index or AUTOCOMMIT connection, and runs fine inside the session transaction.
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_min_prices'))
    db.session.commit()

    count = db.session.execute(text('SELECT COUNT(*) FROM jita_min_prices')).scalar()
    logger.info('jita_min_prices refreshed: %d rows.', count)
    return {'rows': count}


def main():
    parser = argparse.ArgumentParser(description='Refresh the jita_min_prices materialized view.')
    parser.add_argument('-n', '--no-op', action='store_true',
                        help='Dry-run: print current row count, do not refresh.')
    args = parser.parse_args()

    with create_db_app().app_context():
        if args.no_op:
            count = db.session.execute(text('SELECT COUNT(*) FROM jita_min_prices')).scalar()
            logger.info('Dry-run — jita_min_prices currently has %d rows.', count)
            sys.exit(0)
        update_jita_min_prices()


if __name__ == '__main__':
    main()
