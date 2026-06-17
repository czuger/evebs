from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import Blueprint as BlueprintModel, BlueprintModification, EveItem

bp = FlaskBlueprint('blueprint_modifications', __name__)


def _reduction_pct(form):
    """Parse the material reduction percent from the form, clamped to [0, 100].

    Missing/non-numeric input defaults to 0 (no reduction)."""
    try:
        value = float(form.get('reduction_pct') or 0)
    except (ValueError, TypeError):
        return 0.0
    return min(max(value, 0.0), 100.0)


def _load_blueprint(blueprint_id):
    blueprint = db.session.get(BlueprintModel, blueprint_id)
    if blueprint is None:
        abort(404)
    product = EveItem.query.get(blueprint.produced_type_id)
    return blueprint, product


@bp.route('/blueprint_modifications/<int:blueprint_id>')
@login_required
def edit(blueprint_id):
    blueprint, product = _load_blueprint(blueprint_id)
    mod = BlueprintModification.query.filter_by(
        user_id=current_user.id, blueprint_id=blueprint_id).first()
    reduction_pct = round((1 - mod.percent_modification_value) * 100, 2) if mod else 0
    return render_template('blueprint_modifications/edit.html',
                           title=f'Material modifications for {product.name if product else blueprint_id}',
                           blueprint=blueprint,
                           product=product,
                           reduction_pct=reduction_pct)


@bp.route('/blueprint_modifications/<int:blueprint_id>', methods=['POST'])
@login_required
def update(blueprint_id):
    _load_blueprint(blueprint_id)
    multiplier = 1 - _reduction_pct(request.form) / 100.0

    mod = BlueprintModification.query.filter_by(
        user_id=current_user.id, blueprint_id=blueprint_id).first()
    if mod is None:
        mod = BlueprintModification(user_id=current_user.id, blueprint_id=blueprint_id)
        db.session.add(mod)
    mod.percent_modification_value = multiplier
    mod.touched = True
    db.session.commit()

    flash('Material modifications updated.')
    return redirect(url_for('blueprint_modifications.edit', blueprint_id=blueprint_id))
