import logging

from evebs.models import UniverseSystem, EveItem, UniverseRegion
from esi.download_history import _ammo_market_group_ids

logger = logging.getLogger(__name__)

FORGE_REGION_ID = 10000002


def load_reference_data(
    essentials: bool = False,
    forge_only: bool = False,
) -> tuple[dict[int, int], dict[int, int], list]:
    trade_hubs = UniverseSystem.query.filter_by(trade_hub=True).all()
    hub_map = {us.cpp_system_id: us.id for us in trade_hubs}
    item_map = {ei.cpp_eve_item_id: ei.id for ei in EveItem.query.all()}

    hub_region_ids = {
        int(us.universe_constellation.universe_region.cpp_region_id)
        for us in trade_hubs
        if us.universe_constellation and us.universe_constellation.universe_region
    }
    regions = [r for r in UniverseRegion.query.all() if r.cpp_region_id in hub_region_ids]

    if forge_only:
        regions = [r for r in regions if r.cpp_region_id == FORGE_REGION_ID]
        logger.info('[orders] forge-only mode: region %d', FORGE_REGION_ID)

    elif essentials:
        ammo_group_ids = _ammo_market_group_ids()
        ammo_cpp_ids = {
            item.cpp_eve_item_id
            for item in EveItem.query.filter(EveItem.market_group_id.in_(ammo_group_ids)).all()
        }
        item_map = {k: v for k, v in item_map.items() if k in ammo_cpp_ids}
        logger.info('[orders] essentials mode: %d hub regions, %d ammo/charges types',
                    len(regions), len(item_map))

    return hub_map, item_map, regions
