from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from evebs import helpers
from evebs.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    helpers.register(app)

    _register_blueprints(app)

    @app.errorhandler(401)
    def unauthorized(_e):
        return redirect(url_for('auth.login'))

    root = app.config.get('APPLICATION_ROOT', '/')
    if root and root != '/':
        _inner = app.wsgi_app
        def _inject_script_name(environ, start_response):
            path = environ.get('PATH_INFO', '/')
            if path == root or path.startswith(root + '/'):
                environ['PATH_INFO'] = path[len(root):] or '/'
            environ['SCRIPT_NAME'] = root
            return _inner(environ, start_response)
        app.wsgi_app = _inject_script_name

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    return app


def create_db_app(config_class=Config):
    """Minimal Flask app with only config + DB bound — no blueprints, no route imports.

    For standalone scripts that need DB access (``db.session`` / models) without building
    the full web app. Building the web app imports every blueprint, some of which open
    log files at import time (e.g. ``logs/timings.log``) and fail under a script's user or
    permissions in production. See CLAUDE.md.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    return app


def _register_blueprints(app):
    # Imported here (not at module top) on purpose: importing the `evebs` package — which
    # any script doing `from evebs.models import …` / `create_db_app()` triggers — must
    # NOT pull in every route module (they open web log files at import time). This is the
    # one sanctioned exception to the imports-at-top rule; see CLAUDE.md.
    from evebs.routes.admin import bp as admin_bp
    from evebs.routes.auth import bp as auth_bp
    from evebs.routes.buy_orders import bp as buy_orders_bp
    from evebs.routes.choose_trade_hubs import bp as choose_trade_hubs_bp
    from evebs.routes.components_to_buys import bp as components_to_buys_bp
    from evebs.routes.copy_lists import bp as copy_lists_bp
    from evebs.routes.eve_items_saved_lists import bp as eve_items_saved_lists_bp
    from evebs.routes.industry_jobs import bp as industry_jobs_bp
    from evebs.routes.invention_lists import bp as invention_lists_bp
    from evebs.routes.items import bp as items_bp
    from evebs.routes.jita_min_prices import bp as jita_min_prices_bp
    from evebs.routes.price_spreads import bp as price_spreads_bp
    from evebs.routes.price_forecasts import bp as price_forecasts_bp
    from evebs.routes.jita_reactions import bp as jita_reactions_bp
    from evebs.routes.list_items import bp as list_items_bp
    from evebs.routes.main import bp as main_bp
    from evebs.routes.market_data import bp as market_data_bp
    from evebs.routes.market_groups import bp as market_groups_bp
    from evebs.routes.my_assets import bp as my_assets_bp
    from evebs.routes.production_costs import bp as production_costs_bp
    from evebs.routes.production_lists import bp as production_lists_bp
    from evebs.routes.sell_orders import bp as sell_orders_bp
    from evebs.routes.user_blueprints import bp as user_blueprints_bp
    from evebs.routes.user_industry_costs import bp as user_industry_costs_bp
    from evebs.routes.user_sales_orders import bp as user_sales_orders_bp
    from evebs.routes.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(buy_orders_bp)
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
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_blueprints_bp)
    app.register_blueprint(invention_lists_bp)
    app.register_blueprint(copy_lists_bp)
    app.register_blueprint(sell_orders_bp)
    app.register_blueprint(jita_min_prices_bp)
    app.register_blueprint(price_spreads_bp)
    app.register_blueprint(price_forecasts_bp)
    app.register_blueprint(jita_reactions_bp)
    app.register_blueprint(user_industry_costs_bp)
    app.register_blueprint(industry_jobs_bp)
