from evebs.extensions import db

eve_items_users = db.Table('eve_items_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('eve_item_id', db.Integer, db.ForeignKey('eve_items.id')),
)

trade_hubs_users = db.Table('trade_hubs_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('trade_hub_id', db.Integer, db.ForeignKey('trade_hubs.id')),
)

user_blueprints = db.Table('user_blueprints',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('blueprint_id', db.Integer, db.ForeignKey('blueprints.id')),
)
