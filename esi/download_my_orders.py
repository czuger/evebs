import logging
from datetime import datetime

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import EveItem, UniverseStation, UniverseSystem, UserSaleOrder, ProductionList

logger = logging.getLogger(__name__)


class DownloadMyOrders:
    def update(self, user):
        if user.locked:
            logger.debug('%s is locked. Skipping.', user.name)
            return

        client = EsiClient(f'characters/{user.uid}/orders/')
        if not client.set_auth_token(user):
            return

        pages = client.get_all_pages()
        if not pages:
            user.locked = True
            db.session.commit()
            return

        print(pages)

        current_order_ids = [o.id for o in UserSaleOrder.query.filter_by(user_id=user.id).all()]

        for page in pages:
            eve_item_id = EveItem.to_eve_item_id(page['type_id'])
            station = db.session.get(UniverseStation, page['location_id'])
            if station:
                system = (UniverseSystem.query
                          .filter_by(id=station.universe_system_id)
                          .first())
                universe_system_id = system.id if system else None
            else:
                universe_system_id = None

            if not universe_system_id:
                continue

            order = UserSaleOrder.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id, universe_system_id=universe_system_id
            ).first()
            if not order:
                order = UserSaleOrder(user_id=user.id, eve_item_id=eve_item_id,
                                      universe_system_id=universe_system_id, price=page['price'])
                db.session.add(order)
                db.session.flush()
            else:
                order.price = page['price']
                if order.id in current_order_ids:
                    current_order_ids.remove(order.id)

            if user.remove_occuped_places:
                ProductionList.query.filter_by(
                    user_id=user.id, eve_item_id=eve_item_id, universe_system_id=universe_system_id
                ).delete()

        UserSaleOrder.query.filter(UserSaleOrder.id.in_(current_order_ids)).delete(
            synchronize_session=False
        )
        user.download_orders_running = False
        user.last_orders_download = datetime.utcnow()
        db.session.commit()
