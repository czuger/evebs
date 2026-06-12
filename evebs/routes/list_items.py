from flask import Blueprint as FlaskBlueprint, render_template, request, jsonify, abort
from flask_login import current_user, login_required

from evebs.extensions import db
from evebs.models import EveItem, MarketGroup, eve_items_users

bp = FlaskBlueprint('list_items', __name__)


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
    item_ids = request.form.getlist('ids', type=int)
    check_state = request.form.get('check_state') == 'true'
    user_id = current_user.id

    if check_state:
        existing = set(db.session.execute(
            db.select(eve_items_users.c.eve_item_id).where(
                eve_items_users.c.user_id == user_id,
                eve_items_users.c.eve_item_id.in_(item_ids)
            )
        ).scalars().all())
        to_insert = [iid for iid in item_ids if iid not in existing]
        if to_insert:
            db.session.execute(
                eve_items_users.insert(),
                [{'user_id': user_id, 'eve_item_id': iid} for iid in to_insert]
            )
    else:
        db.session.execute(
            eve_items_users.delete().where(
                eve_items_users.c.user_id == user_id,
                eve_items_users.c.eve_item_id.in_(item_ids)
            )
        )

    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/list_items/select_group', methods=['POST'])
@login_required
def select_group():
    group_id = request.form.get('group_id', type=int)
    check_state = request.form.get('check_state', 'true') == 'true'
    group = MarketGroup.query.get_or_404(group_id)
    item_ids = _collect_item_ids(group)
    user_id = current_user.id

    if check_state:
        existing = set(db.session.execute(
            db.select(eve_items_users.c.eve_item_id).where(
                eve_items_users.c.user_id == user_id,
                eve_items_users.c.eve_item_id.in_(item_ids)
            )
        ).scalars().all())
        to_insert = [iid for iid in item_ids if iid not in existing]
        if to_insert:
            db.session.execute(
                eve_items_users.insert(),
                [{'user_id': user_id, 'eve_item_id': iid} for iid in to_insert]
            )
    else:
        db.session.execute(
            eve_items_users.delete().where(
                eve_items_users.c.user_id == user_id,
                eve_items_users.c.eve_item_id.in_(item_ids)
            )
        )

    db.session.commit()
    return jsonify({'ok': True, 'count': len(item_ids)})
