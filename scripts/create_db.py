#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evebs import create_app, init_db

parser = argparse.ArgumentParser(description="Initialise the evebs database.")
parser.add_argument(
    "--recreate",
    action="store_true",
    help="Drop all tables and views, then recreate from scratch.",
)
args = parser.parse_args()

app = create_app()
init_db(app, recreate=args.recreate)
print("Database recreated." if args.recreate else "Database initialised.")
