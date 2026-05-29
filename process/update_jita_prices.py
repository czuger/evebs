#!/usr/bin/env python3
"""Refresh the jita_prices materialized view."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Refresh the jita_prices materialized view.')
parser.add_argument('-n', '--no-op', action='store_true',
                    help='Dry-run: print current row count, do not refresh.')
args = parser.parse_args()

from app import app

with app.app_context():
    from sqlalchemy import text
    from evebs.extensions import db

    if args.no_op:
        count = db.session.execute(text('SELECT COUNT(*) FROM jita_prices')).scalar()
        logger.info('Dry-run — jita_prices currently has %d rows.', count)
        sys.exit(0)

    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_prices'))
    db.session.commit()
    count = db.session.execute(text('SELECT COUNT(*) FROM jita_prices')).scalar()
    logger.info('jita_prices refreshed: %d rows.', count)
