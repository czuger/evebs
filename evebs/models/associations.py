from evebs.extensions import db

eve_items_users = db.Table('eve_items_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('eve_item_id', db.Integer, db.ForeignKey('universe_types.id')),
)

trade_hubs_users = db.Table('trade_hubs_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('trade_hub_id', db.Integer, db.ForeignKey('trade_hubs.id')),
)
