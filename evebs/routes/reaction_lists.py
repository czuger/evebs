from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import Blueprint as BlueprintModel, EveItem, ReactionList

bp = FlaskBlueprint('reaction_lists', __name__)

# Fuel blocks are treated as leaves (bought, not decomposed) in the reaction tree:
# Nitrogen / Hydrogen / Helium / Oxygen Fuel Block.
FUEL_BLOCK_IDS = {4051, 4246, 4247, 4312}


def _decompose(chain, parent_units, parent_prod_qtt, root_runs, rxn_ids, prodqtt):
    """Recursively turn a manufacturing_tree chain into display nodes.

    Sub-reaction `runs` match the parent reaction-list entry's run count (`root_runs`), so a
    checked sub-reaction is added with the same number of runs as its parent. `units` is the
    effective total quantity of each material needed (chain `quantity` is per one batch of the
    immediate parent, so it propagates as quantity * parent_units / parent_prod_qtt).
    """
    nodes = []
    for mid_str, d in chain.items():
        mid = int(mid_str)
        units = d['quantity'] * parent_units / parent_prod_qtt if parent_prod_qtt else 0
        p = prodqtt.get(mid)
        is_rxn = mid in rxn_ids
        runs = root_runs if is_rxn else None
        children = (_decompose(d['chain'], units, p, root_runs, rxn_ids, prodqtt)
                    if (d.get('chain') and p and mid not in FUEL_BLOCK_IDS) else [])
        nodes.append(SimpleNamespace(item_id=mid, name=d['name'], qty=d['quantity'],
                                     units=units, is_reaction=is_rxn, runs=runs,
                                     children=children))
    return nodes


def _has_reaction(nodes):
    return any(n.is_reaction or _has_reaction(n.children) for n in nodes)


@bp.route('/reaction_lists/edit')
@login_required
def edit():
    user = current_user
    reaction_lists = (ReactionList.query.filter_by(user_id=user.id)
                      .join(EveItem, EveItem.id == ReactionList.eve_item_id)
                      .order_by(EveItem.name).all())

    rxn_ids = {bp_id for (bp_id,) in db.session.query(BlueprintModel.produced_type_id)
               .filter(BlueprintModel.activity_type == 'reaction').all()}
    prodqtt = {pid: qtt for pid, qtt in
               db.session.query(BlueprintModel.produced_type_id, BlueprintModel.prod_qtt).all()}

    entries = []
    for rl in reaction_lists:
        bp_obj = rl.eve_item.blueprint if rl.eve_item else None
        tree = []
        if bp_obj and bp_obj.manufacturing_tree:
            root_runs = rl.runs_count or 1
            root_units = bp_obj.prod_qtt * root_runs
            tree = _decompose(bp_obj.manufacturing_tree, root_units, bp_obj.prod_qtt,
                              root_runs, rxn_ids, prodqtt)
        entries.append(SimpleNamespace(rl=rl, tree=tree, has_reactions=_has_reaction(tree)))

    return render_template('reaction_lists/edit.html',
                           title='Reaction list',
                           reaction_lists=reaction_lists,
                           entries=entries,
                           user=user)


@bp.route('/reaction_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    runs_count = request.form.get('runs_count', 10, type=int)

    existing = ReactionList.query.filter_by(user_id=user.id, eve_item_id=eve_item_id).first()
    if not existing:
        db.session.add(ReactionList(user_id=user.id, eve_item_id=eve_item_id, runs_count=runs_count))
        db.session.commit()
        flash('Added to reaction list.', 'success')
    else:
        flash('Already in reaction list.', 'info')
    return redirect(request.referrer or url_for('reaction_lists.edit'))


@bp.route('/reaction_lists/add_subreactions', methods=['POST'])
@login_required
def add_subreactions():
    user = current_user
    added = 0
    for item_id in request.form.getlist('sub_item', type=int):
        runs = request.form.get(f'sub_runs_{item_id}', 1, type=int)
        existing = ReactionList.query.filter_by(user_id=user.id, eve_item_id=item_id).first()
        if not existing:
            db.session.add(ReactionList(user_id=user.id, eve_item_id=item_id,
                                        runs_count=max(runs, 1)))
            added += 1
    db.session.commit()
    flash(f'Added {added} sub-reaction(s) to the reaction list.'
          if added else 'No new sub-reactions added.',
          'success' if added else 'info')
    return redirect(url_for('reaction_lists.edit'))


@bp.route('/reaction_lists/update', methods=['POST'])
@login_required
def update():
    user = current_user
    for key, value in request.form.items():
        if key.startswith('runs_count_'):
            rl_id = int(key.split('_')[-1])
            rl = ReactionList.query.get(rl_id)
            if rl and rl.user_id == user.id:
                try:
                    rl.runs_count = int(value)
                except ValueError:
                    pass
    db.session.commit()
    return redirect(url_for('reaction_lists.edit'))


@bp.route('/reaction_lists/clear_all', methods=['POST'])
@login_required
def clear_all():
    ReactionList.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Reaction list cleared.', 'success')
    return redirect(url_for('reaction_lists.edit'))


@bp.route('/remove_reaction_list_check', methods=['POST'])
@login_required
def remove_check():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    ReactionList.query.filter_by(user_id=user.id, eve_item_id=eve_item_id).delete()
    db.session.commit()
    flash('Removed from reaction list.', 'success')
    return redirect(url_for('reaction_lists.edit'))
