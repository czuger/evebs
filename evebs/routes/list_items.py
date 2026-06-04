from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import current_user, login_required

from evebs.extensions import db
from evebs.models import EveItem, MarketGroup

bp = Blueprint('list_items', __name__)


def _collect_item_ids(group):
    if group.is_leaf():
        return [item.id for item in group.eve_items]
    result = []
    for child in group.children:
        result.extend(_collect_item_ids(child))
    return result


@bp.route('/list_items')
def show():
    group_id = request.args.get('group_id', type=int)
    user = current_user if current_user.is_authenticated else None

    item_ids = set()
    if user:
        item_ids = set(user.eve_item_ids)

    if group_id:
        current_group = MarketGroup.query.get_or_404(group_id)
        if current_group.is_leaf():
            items = EveItem.query.filter_by(market_group_id=group_id).order_by(
                EveItem.faction, EveItem.name
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
                           user=user)


@bp.route('/list_items/selection_change', methods=['POST'])
@login_required
def selection_change():
    item_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    item = EveItem.query.get_or_404(item_id)
    user = current_user
    if check_state:
        if item not in user.eve_items:
            user.eve_items.append(item)
    else:
        if item in user.eve_items:
            user.eve_items.remove(item)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/list_items/select_group', methods=['POST'])
@login_required
def select_group():
    group_id = request.form.get('group_id', type=int)
    group = MarketGroup.query.get_or_404(group_id)
    item_ids = _collect_item_ids(group)
    items = EveItem.query.filter(EveItem.id.in_(item_ids)).all()
    user = current_user
    for item in items:
        if item not in user.eve_items:
            user.eve_items.append(item)
    db.session.commit()
    return jsonify({'ok': True, 'count': len(item_ids)})
