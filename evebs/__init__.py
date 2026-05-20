from flask import Flask
from config import Config
from evebs.extensions import db, migrate, login_manager
from evebs import helpers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    import redis as _redis
    import evebs.extensions as _ext
    _ext.redis_client = _redis.from_url(app.config['REDIS_URL'], decode_responses=True)

    helpers.register(app)

    from evebs.routes.auth import bp as auth_bp
    from evebs.routes.main import bp as main_bp
    from evebs.routes.buy_orders import bp as buy_orders_bp
    from evebs.routes.price_advices import bp as price_advices_bp
    from evebs.routes.items import bp as items_bp
    from evebs.routes.list_items import bp as list_items_bp
    from evebs.routes.production_costs import bp as production_costs_bp
    from evebs.routes.production_lists import bp as production_lists_bp
    from evebs.routes.user_sales_orders import bp as user_sales_orders_bp
    from evebs.routes.users import bp as users_bp
    from evebs.routes.choose_trade_hubs import bp as choose_trade_hubs_bp
    from evebs.routes.components_to_buys import bp as components_to_buys_bp
    from evebs.routes.market_data import bp as market_data_bp
    from evebs.routes.market_groups import bp as market_groups_bp
    from evebs.routes.eve_items_saved_lists import bp as eve_items_saved_lists_bp
    from evebs.routes.my_assets import bp as my_assets_bp
    from evebs.routes.blueprints import bp as blueprints_bp
    from evebs.routes.my_blueprints import bp as my_blueprints_bp
    from evebs.routes.admin import bp as admin_bp
    from evebs.routes.industry import bp as industry_bp
    from evebs.routes.planetary import bp as planetary_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(buy_orders_bp)
    app.register_blueprint(price_advices_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(list_items_bp)
    app.register_blueprint(production_costs_bp)
    app.register_blueprint(production_lists_bp)
    app.register_blueprint(user_sales_orders_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(choose_trade_hubs_bp)
    app.register_blueprint(components_to_buys_bp)
    app.register_blueprint(market_data_bp)
    app.register_blueprint(market_groups_bp)
    app.register_blueprint(eve_items_saved_lists_bp)
    app.register_blueprint(my_assets_bp)
    app.register_blueprint(blueprints_bp)
    app.register_blueprint(my_blueprints_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(industry_bp)
    app.register_blueprint(planetary_bp)

    return app
