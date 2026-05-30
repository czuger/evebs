#!/usr/bin/env python3
import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import setup_logging
setup_logging()

parser = argparse.ArgumentParser(description='Download public market orders from ESI and upsert into DB.')
parser.add_argument('-e', '--essentials', action='store_true',
                    help='Restrict to trade-hub regions and ammo/charges types only.')
parser.add_argument('-f', '--forge', action='store_true',
                    help='Download only The Forge region (Jita). Takes precedence over --essentials.')
parser.add_argument('-a', '--all-at-once', action='store_true',
                    help='Fetch all orders per region in one bulk call instead of per type_id.')
args = parser.parse_args()

from app import app
with app.app_context():
    from esi.download_public_orders import download
    download(essentials=args.essentials, forge_only=args.forge, all_at_once=args.all_at_once)
