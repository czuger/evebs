from esi.client import EsiClient


class DownloadMyOrders:
    def update(self, user):
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

        from evebs.models import EveItem, UniverseStation, TradeHub, UserSaleOrder, ProductionList
        from evebs.extensions import db
        from datetime import datetime

        current_order_ids = [o.id for o in UserSaleOrder.query.filter_by(user_id=user.id).all()]

        for page in pages:
            eve_item_id = EveItem.to_eve_item_id(page['type_id'])
            us = UniverseStation.query.filter_by(cpp_station_id=page['location_id']).first()
            if us and us.universe_system:
                hub = TradeHub.query.filter_by(eve_system_id=us.universe_system.cpp_system_id).first()
                trade_hub_id = hub.id if hub else None
            else:
                trade_hub_id = None

            if not trade_hub_id:
                continue

            order = UserSaleOrder.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id, trade_hub_id=trade_hub_id
            ).first()
            if not order:
                order = UserSaleOrder(user_id=user.id, eve_item_id=eve_item_id,
                                      trade_hub_id=trade_hub_id, price=page['price'])
                db.session.add(order)
                db.session.flush()
            else:
                order.price = page['price']
                if order.id in current_order_ids:
                    current_order_ids.remove(order.id)

            if user.remove_occuped_places:
                ProductionList.query.filter_by(
                    user_id=user.id, eve_item_id=eve_item_id, trade_hub_id=trade_hub_id
                ).delete()

        UserSaleOrder.query.filter(UserSaleOrder.id.in_(current_order_ids)).delete(
            synchronize_session=False
        )
        user.download_orders_running = False
        user.last_orders_download = datetime.utcnow()
        db.session.commit()
