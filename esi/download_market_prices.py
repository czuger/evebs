"""Download global market adjusted/average prices from ESI and upsert into market_prices."""
from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import MarketPrice, UniverseType


def download_market_prices():
    print('Fetching market prices from ESI...')
    rows = EsiClient('markets/prices/').get_all_pages()
    print(f'  {len(rows)} entries received. Upserting...')

    known_type_ids = {r[0] for r in db.session.query(UniverseType.id).all()}

    created = updated = skipped = 0
    for i, row in enumerate(rows, 1):
        type_id = row.get('type_id')
        if not type_id or type_id not in known_type_ids:
            skipped += 1
            continue
        price = MarketPrice.query.filter_by(type_id=type_id).first()
        if price:
            price.adjusted_price = row.get('adjusted_price')
            price.average_price = row.get('average_price')
            updated += 1
        else:
            db.session.add(MarketPrice(
                type_id=type_id,
                adjusted_price=row.get('adjusted_price'),
                average_price=row.get('average_price'),
            ))
            created += 1
        if i % 1000 == 0:
            print(f'  {i}/{len(rows)}...')

    db.session.commit()
    print(f'Done. Created: {created}, updated: {updated}, skipped (unknown type): {skipped}.')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        download_market_prices()
