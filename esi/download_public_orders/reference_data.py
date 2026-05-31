import logging

from evebs.models import UniverseSystem, EveItem, UniverseRegion
from esi.download_history import _ammo_market_group_ids

logger = logging.getLogger(__name__)

FORGE_REGION_ID = 10000002


def load_reference_data(
    essentials: bool = False,
    forge_only: bool = False,
    regions: str = 'hub',
) -> tuple[dict[int, int], dict[int, int], list]:
    """Load reference data for order downloads.

    regions: 'hub'     — only regions containing a trade-hub system (default)
             'non_hub' — only regions with no trade-hub system
             'all'     — every region
    """
    trade_hubs = UniverseSystem.query.filter_by(trade_hub=True).all()
    hub_map = {us.cpp_system_id: us.id for us in trade_hubs}
    item_map = {ei.id: ei.id for ei in EveItem.query.all()}

    hub_region_ids = {
        int(us.universe_constellation.universe_region.cpp_region_id)
        for us in trade_hubs
        if us.universe_constellation and us.universe_constellation.universe_region
    }
    all_regions = UniverseRegion.query.all()
    if regions == 'hub':
        region_list = [r for r in all_regions if r.cpp_region_id in hub_region_ids]
    elif regions == 'non_hub':
        region_list = [r for r in all_regions if r.cpp_region_id not in hub_region_ids]
    else:
        region_list = all_regions

    if forge_only:
        region_list = [r for r in region_list if r.cpp_region_id == FORGE_REGION_ID]
        logger.info('[orders] forge-only mode: region %d', FORGE_REGION_ID)

    elif essentials:
        ammo_group_ids = _ammo_market_group_ids()
        ammo_cpp_ids = {
            item.id
            for item in EveItem.query.filter(EveItem.market_group_id.in_(ammo_group_ids)).all()
        }
        item_map = {k: v for k, v in item_map.items() if k in ammo_cpp_ids}
        logger.info('[orders] essentials mode: %d hub regions, %d ammo/charges types',
                    len(region_list), len(item_map))

    return hub_map, item_map, region_list
