from evebs.extensions import db

eve_items_users = db.Table('eve_items_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('eve_item_id', db.Integer, db.ForeignKey('universe_types.id')),
)

universe_systems_users = db.Table('universe_systems_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('universe_system_id', db.BigInteger, db.ForeignKey('universe_systems.id')),
)
