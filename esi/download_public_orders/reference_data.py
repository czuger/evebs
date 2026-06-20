import logging

from evebs.extensions import db
from evebs.models import UniverseSystem, EveItem, UniverseRegion, MarketGroup

logger = logging.getLogger(__name__)

FORGE_REGION_ID = 10000002


def _ammo_market_group_ids(session):
    all_groups = session.query(MarketGroup).all()
    children_map = {}
    for g in all_groups:
        children_map.setdefault(g.id, [])
        if g.parent_id is not None:
            children_map.setdefault(g.parent_id, []).append(g.id)

    roots = [g.id for g in all_groups if g.name and 'Ammunition' in g.name and g.parent_id is None]

    result = set()
    stack = list(roots)
    while stack:
        gid = stack.pop()
        result.add(gid)
        stack.extend(children_map.get(gid, []))
    return result


def load_reference_data(
    essentials: bool = False,
    forge_only: bool = False,
    regions: str = 'hub',
    session=None,
) -> tuple[dict[int, int], dict[int, int], list]:
    """Load reference data for order downloads.

    regions: 'hub'     — only regions containing a trade-hub system (default)
             'non_hub' — only regions with no trade-hub system
             'all'     — every region
    """
    session = session or db.session
    trade_hubs = session.query(UniverseSystem).filter_by(trade_hub=True).all()
    hub_map = {us.id: us.id for us in trade_hubs}
    item_map = {ei.id: ei.id for ei in session.query(EveItem).all()}

    hub_region_ids = {
        us.universe_constellation.universe_region.id
        for us in trade_hubs
        if us.universe_constellation and us.universe_constellation.universe_region
    }
    all_regions = session.query(UniverseRegion).all()
    if regions == 'hub':
        region_list = [r for r in all_regions if r.id in hub_region_ids]
    elif regions == 'non_hub':
        region_list = [r for r in all_regions if r.id not in hub_region_ids]
    else:
        region_list = all_regions

    if forge_only:
        region_list = [r for r in region_list if r.id == FORGE_REGION_ID]
        logger.info('[orders] forge-only mode: region %d', FORGE_REGION_ID)

    elif essentials:
        ammo_group_ids = _ammo_market_group_ids(session)
        ammo_cpp_ids = {
            item.id
            for item in session.query(EveItem).filter(EveItem.market_group_id.in_(ammo_group_ids)).all()
        }
        item_map = {k: v for k, v in item_map.items() if k in ammo_cpp_ids}
        logger.info('[orders] essentials mode: %d hub regions, %d ammo/charges types',
                    len(region_list), len(item_map))

    return hub_map, item_map, region_list
