import json

from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import current_user, login_required

from evebs.extensions import db, redis_client
from evebs.models import MarketGroup, UniverseType

bp = Blueprint('list_items', __name__)

_SEARCH_CACHE_KEY = 'list_items:search_data'
_SEARCH_CACHE_TTL = 48 * 3600


@bp.route('/list_items')
def show():
    """Render the market group browser and item toggle list."""
    group_id = request.args.get('group_id', type=int)
    user = current_user if current_user.is_authenticated else None

    item_ids = set()
    if user:
        item_ids = set(user.eve_item_ids)

    cached = redis_client.get(_SEARCH_CACHE_KEY)
    if cached:
        search_data = json.loads(cached)
    else:
        all_items = (UniverseType.query
                     .filter(UniverseType.market_group_id.isnot(None))
                     .with_entities(UniverseType.id, UniverseType.name)
                     .order_by(UniverseType.name)
                     .all())
        search_data = {r.name: r.id for r in all_items}
        redis_client.setex(_SEARCH_CACHE_KEY, _SEARCH_CACHE_TTL, json.dumps(search_data))

    if group_id:
        current_group = MarketGroup.query.get_or_404(group_id)
        if current_group.is_leaf():
            items = UniverseType.query.filter_by(market_group_id=group_id).order_by(
                UniverseType.name
            ).all()
            groups = None
        else:
            items = None
            groups = current_group.children
            groups = sorted(groups, key=lambda g: g.name)
    else:
        current_group = None
        groups = sorted(MarketGroup.roots().all(), key=lambda g: g.name)
        items = None

    return render_template('list_items/show.html',
                           title='Items list',
                           current_group=current_group,
                           groups=groups,
                           items=items,
                           item_ids=item_ids,
                           search_data=search_data,
                           user=user)


@bp.route('/list_items/selection_change', methods=['POST'])
@login_required
def selection_change():
    """Add or remove an item from the user's watchlist via AJAX."""
    item_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    item = UniverseType.query.get_or_404(item_id)
    user = current_user
    if check_state:
        if item not in user.eve_items:
            user.eve_items.append(item)
    else:
        if item in user.eve_items:
            user.eve_items.remove(item)
    db.session.commit()
    return jsonify({'ok': True})
