"""Update prices_mins, buy_orders_analytics, prices_advices from trade order data."""
from datetime import datetime, timedelta, date
from sqlalchemy import text
from evebs.extensions import db


def update_prices_min():
    print('Updating min prices...')
    now = datetime.utcnow()

    # Remove entries with no sell orders
    db.session.execute(text("""
        DELETE FROM prices_mins WHERE NOT EXISTS (
            SELECT 1 FROM public_trade_orders pto
            WHERE prices_mins.trade_hub_id = pto.trade_hub_id
            AND prices_mins.eve_item_id = pto.eve_item_id
            AND pto.is_buy_order = 0
        )
    """))

    # Insert / update min prices
    db.session.execute(text("""
        INSERT INTO prices_mins (trade_hub_id, eve_item_id, min_price, created_at, updated_at)
        SELECT trade_hub_id, eve_item_id, MIN(price), :now, :now
        FROM public_trade_orders
        WHERE is_buy_order = 0
        GROUP BY trade_hub_id, eve_item_id
        ON CONFLICT (trade_hub_id, eve_item_id)
        DO UPDATE SET min_price = excluded.min_price, updated_at = :now
    """), {'now': now})

    db.session.commit()
    print('Min prices updated.')


def update_buy_orders_analytics():
    print('Updating buy orders analytics...')
    now = datetime.utcnow()

    db.session.execute(text("""
        INSERT INTO buy_orders_analytics (trade_hub_id, eve_item_id, approx_max_price, created_at, updated_at)
        SELECT trade_hub_id, eve_item_id, MAX(price) * 0.9, :now, :now
        FROM public_trade_orders
        WHERE is_buy_order = 1
        GROUP BY trade_hub_id, eve_item_id
        ON CONFLICT (trade_hub_id, eve_item_id)
        DO UPDATE SET approx_max_price = excluded.approx_max_price, updated_at = :now
    """), {'now': now})

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET over_approx_max_price_volume = (
            SELECT SUM(volume_remain)
            FROM public_trade_orders bo
            WHERE bo.price >= buy_orders_analytics.approx_max_price
            AND bo.trade_hub_id = buy_orders_analytics.trade_hub_id
            AND bo.eve_item_id = buy_orders_analytics.eve_item_id
            AND bo.is_buy_order = 1
        )
    """))

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET
            single_unit_cost = (
                SELECT cost FROM eve_items WHERE eve_items.id = buy_orders_analytics.eve_item_id
            ),
            single_unit_margin = approx_max_price - (
                SELECT cost FROM eve_items WHERE eve_items.id = buy_orders_analytics.eve_item_id
            )
        WHERE EXISTS (
            SELECT 1 FROM eve_items WHERE eve_items.id = buy_orders_analytics.eve_item_id
        )
    """))

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET
            estimated_volume_margin = single_unit_margin * over_approx_max_price_volume,
            final_margin = LEAST(
                single_unit_margin * over_approx_max_price_volume,
                single_unit_margin * (
                    SELECT nb_runs * prod_qtt FROM blueprints
                    JOIN eve_items ON eve_items.blueprint_id = blueprints.id
                    WHERE eve_items.id = buy_orders_analytics.eve_item_id
                )
            )
        WHERE single_unit_margin IS NOT NULL
    """))

    db.session.commit()
    print('Buy orders analytics updated.')


def update_prices_advices_immediate():
    print('Updating prices advices (immediate)...')
    now = datetime.utcnow()

    # Clear advices for items with no blueprint
    db.session.execute(text("""
        DELETE FROM prices_advices WHERE eve_item_id IN (
            SELECT id FROM eve_items WHERE blueprint_id IS NULL
        )
    """))

    # Insert missing combinations from sales_finals
    db.session.execute(text("""
        INSERT INTO prices_advices (eve_item_id, trade_hub_id, created_at, updated_at)
        SELECT DISTINCT sf.eve_item_id, sf.trade_hub_id, :now, :now
        FROM sales_finals sf
        JOIN eve_items ei ON sf.eve_item_id = ei.id
        WHERE ei.blueprint_id IS NOT NULL
        ON CONFLICT (eve_item_id, trade_hub_id) DO NOTHING
    """), {'now': now})

    # Clear where no sales data
    db.session.execute(text("""
        UPDATE prices_advices SET vol_month = NULL, avg_price_month = NULL,
            immediate_montly_pcent = NULL, margin_percent = NULL, avg_price_week = NULL,
            updated_at = :now
        WHERE NOT EXISTS (
            SELECT 1 FROM sales_finals sf
            WHERE sf.trade_hub_id = prices_advices.trade_hub_id
            AND sf.eve_item_id = prices_advices.eve_item_id
        )
    """), {'now': now})

    # Update vol_month and avg_price_month
    db.session.execute(text("""
        UPDATE prices_advices SET
            vol_month = (
                SELECT SUM(sf.volume) FROM sales_finals sf
                WHERE sf.trade_hub_id = prices_advices.trade_hub_id
                AND sf.eve_item_id = prices_advices.eve_item_id
            ),
            avg_price_month = (
                SELECT AVG(sf.price) FROM sales_finals sf
                WHERE sf.trade_hub_id = prices_advices.trade_hub_id
                AND sf.eve_item_id = prices_advices.eve_item_id
            ),
            updated_at = :now
    """), {'now': now})

    # Update avg_price_week (last 7 days)
    cutoff = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    db.session.execute(text("""
        UPDATE prices_advices SET
            avg_price_week = (
                SELECT SUM(sf.volume * sf.price) / SUM(sf.volume)
                FROM sales_finals sf
                WHERE sf.trade_hub_id = prices_advices.trade_hub_id
                AND sf.eve_item_id = prices_advices.eve_item_id
                AND sf.day >= :cutoff
                AND sf.volume > 0
            ),
            updated_at = :now
        WHERE EXISTS (
            SELECT 1 FROM sales_finals sf
            WHERE sf.trade_hub_id = prices_advices.trade_hub_id
            AND sf.eve_item_id = prices_advices.eve_item_id
        )
    """), {'now': now, 'cutoff': cutoff})

    # Update margin_percent
    db.session.execute(text("""
        UPDATE prices_advices SET
            margin_percent = (
                SELECT (pm.min_price / ei.cost - 1.0)
                FROM prices_mins pm, eve_items ei
                WHERE pm.eve_item_id = prices_advices.eve_item_id
                AND pm.trade_hub_id = prices_advices.trade_hub_id
                AND ei.id = prices_advices.eve_item_id
                AND ei.cost IS NOT NULL
                AND ei.cost > 0
            ),
            immediate_montly_pcent = (
                SELECT pm.min_price / prices_advices.avg_price_month
                FROM prices_mins pm
                WHERE pm.eve_item_id = prices_advices.eve_item_id
                AND pm.trade_hub_id = prices_advices.trade_hub_id
                AND prices_advices.avg_price_month IS NOT NULL
                AND prices_advices.avg_price_month > 0
            ),
            updated_at = :now
        WHERE vol_month IS NOT NULL
    """), {'now': now})

    db.session.commit()
    print('Prices advices updated.')


def update_weekly_price_details():
    print('Updating weekly price details...')
    now = datetime.utcnow()
    yesterday = (now.date() - timedelta(days=1)).isoformat()
    week_ago = (now.date() - timedelta(days=7)).isoformat()

    db.session.execute(text("""
        INSERT INTO weekly_price_details (eve_item_id, trade_hub_id, day, volume, weighted_avg_price, created_at, updated_at)
        SELECT sf.eve_item_id, sf.trade_hub_id, sf.day,
               SUM(sf.volume),
               SUM(sf.volume * sf.price) / SUM(sf.volume),
               :now, :now
        FROM sales_finals sf
        WHERE sf.day > :yesterday AND sf.volume > 0
        GROUP BY sf.eve_item_id, sf.trade_hub_id, sf.day
        ON CONFLICT (eve_item_id, trade_hub_id, day)
        DO UPDATE SET
            volume = excluded.volume,
            weighted_avg_price = excluded.weighted_avg_price,
            updated_at = :now
    """), {'now': now, 'yesterday': yesterday})

    db.session.execute(text("""
        DELETE FROM weekly_price_details WHERE day < :week_ago
    """), {'week_ago': week_ago})

    # Update weekly_avg_price on eve_items from Jita (system 30000142)
    db.session.execute(text("""
        UPDATE eve_items SET weekly_avg_price = (
            SELECT SUM(wpd.volume * wpd.weighted_avg_price) / SUM(wpd.volume)
            FROM weekly_price_details wpd
            JOIN trade_hubs tu ON wpd.trade_hub_id = tu.id
            WHERE tu.eve_system_id = 30000142
            AND wpd.eve_item_id = eve_items.id
        ), updated_at = :now
    """), {'now': now})

    db.session.commit()
    print('Weekly price details updated.')


def update_market_histories():
    print('Updating market history groups...')
    import glob
    import json
    from evebs.models import EveMarketHistoriesGroup, UniverseRegion

    region_ids = {r.id for r in UniverseRegion.query.all()}
    from evebs.models import UniverseType
    item_map = {str(i.id): i.id for i in UniverseType.query.all()}

    for filepath in glob.glob('data/regional_sales_volumes_*.json_stream'):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                region_id = rec.get('region_id')
                if region_id not in region_ids:
                    region_id = None
                item_id = item_map.get(str(rec.get('cpp_type_id')))
                if not region_id or not item_id:
                    continue

                entry = EveMarketHistoriesGroup.query.filter_by(
                    eve_item_id=item_id, universe_region_id=region_id
                ).first()
                if entry:
                    entry.volume = rec.get('volume', 0)
                    entry.average = rec.get('avg')
                    entry.highest = rec.get('max')
                    entry.lowest = rec.get('min')
                else:
                    entry = EveMarketHistoriesGroup(
                        eve_item_id=item_id,
                        universe_region_id=region_id,
                        volume=rec.get('volume', 0),
                        average=rec.get('avg'),
                        highest=rec.get('max'),
                        lowest=rec.get('min'),
                    )
                    db.session.add(entry)

    db.session.commit()
    print('Market history groups updated.')
