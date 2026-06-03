#!/usr/bin/env python3
"""Refresh the jita_reaction_margins materialized view."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Refresh the jita_reaction_margins materialized view.')
parser.add_argument('-n', '--no-op', action='store_true',
                    help='Dry-run: print current row count, do not refresh.')
args = parser.parse_args()

from app import app

with app.app_context():
    from sqlalchemy import text
    from evebs.extensions import db

    if args.no_op:
        count = db.session.execute(text('SELECT COUNT(*) FROM jita_reaction_margins')).scalar()
        logger.info('Dry-run — jita_reaction_margins currently has %d rows.', count)
        sys.exit(0)

    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_reaction_margins'))
    db.session.commit()
    count = db.session.execute(text('SELECT COUNT(*) FROM jita_reaction_margins')).scalar()
    logger.info('jita_reaction_margins refreshed: %d rows.', count)
