#!/usr/bin/env python3
"""
Load public trade orders from a CSV file into the database.

Usage:
  python scripts/load_orders_from_csv.py <path/to/orders.csv>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if len(sys.argv) != 2:
    print(__doc__)
    sys.exit(1)

filepath = sys.argv[1]
if not os.path.isfile(filepath):
    print(f'Error: file not found: {filepath}')
    sys.exit(1)

from evebs import create_app
from esi.download_public_orders import DownloadPublicTradesOrders

app = create_app()
with app.app_context():
    DownloadPublicTradesOrders(verbose=True).load_from_csv(filepath)
