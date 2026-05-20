from esi.client import EsiClient


class DownloadMyOrders:
    """Download a character's open sell orders from ESI and sync UserSaleOrder records."""

    def update(self, user):
        """Sync sell orders for the given user, removing stale entries."""
        if user.locked:
            print(f'{user.name} is locked. Skipping.')
            return

        client = EsiClient(f'characters/{user.uid}/orders/')
        if not client.set_auth_token(user):
            return

        pages = client.get_all_pages()
        if not pages:
            user.locked = True
            from evebs.extensions import db
            db.session.commit()
            return

        from evebs.models import UniverseStation, UniverseSystem, UserSaleOrder, ProductionList
        from evebs.extensions import db
        from datetime import datetime

        current_order_ids = [o.id for o in UserSaleOrder.query.filter_by(user_id=user.id).all()]

        for page in pages:
            eve_item_id = page['type_id']
            us = UniverseStation.query.filter_by(id=page['location_id']).first()
            system_id = us.universe_system_id if us else None

            if not system_id:
                continue

            order = UserSaleOrder.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id, system_id=system_id
            ).first()
            if not order:
                order = UserSaleOrder(user_id=user.id, eve_item_id=eve_item_id,
                                      system_id=system_id, price=page['price'])
                db.session.add(order)
                db.session.flush()
            else:
                order.price = page['price']
                if order.id in current_order_ids:
                    current_order_ids.remove(order.id)

            if user.remove_occuped_places:
                ProductionList.query.filter_by(
                    user_id=user.id, eve_item_id=eve_item_id, system_id=system_id
                ).delete()

        UserSaleOrder.query.filter(UserSaleOrder.id.in_(current_order_ids)).delete(
            synchronize_session=False
        )
        user.download_orders_running = False
        user.last_orders_download = datetime.utcnow()
        db.session.commit()
