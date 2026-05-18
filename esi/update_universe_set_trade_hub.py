"""Determine trade hub systems from market order volume and set the trade_hub flag."""
from sqlalchemy import func

from evebs.extensions import db
from evebs.models import UniverseSystem, MarketOrder, UniverseStation


def update_universe_set_trade_hub():
    """Set trade_hub=True on the top 6 highsec systems by market order volume."""
    rows = (
        db.session.query(
            MarketOrder.system_id,
            UniverseSystem.name,
            func.sum(MarketOrder.volume_total).label('total_volume'),
        )
        .join(UniverseSystem, UniverseSystem.id == MarketOrder.system_id)
        .join(UniverseStation, UniverseStation.id == MarketOrder.location_id)
        .filter(UniverseSystem.security_status >= 0.5)
        .group_by(MarketOrder.system_id, UniverseSystem.name)
        .order_by(func.sum(MarketOrder.volume_total).desc())
        .limit(6)
        .all()
    )

    top_ids = [r.system_id for r in rows]

    UniverseSystem.query.update({'trade_hub': False})
    db.session.flush()

    UniverseSystem.query.filter(UniverseSystem.id.in_(top_ids)).update(
        {'trade_hub': True}, synchronize_session=False
    )
    db.session.commit()

    print(f'Trade hubs set ({len(top_ids)}):')
    for r in rows:
        print(f'  {r.name} — {int(r.total_volume):,} volume')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        update_universe_set_trade_hub()
