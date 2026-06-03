from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from evebs.models import JitaReactionMargins, EveItem
from evebs.models import Blueprint as BlueprintModel

bp = Blueprint('jita_reactions', __name__)
PER_PAGE = 20


@bp.route('/jita_reactions')
@login_required
def show():
    page = request.args.get('page', 1, type=int)

    user_bp_ids = [b.id for b in current_user.blueprints]

    q = (
        JitaReactionMargins.query
        .options(joinedload(JitaReactionMargins.eve_item).joinedload(EveItem.market_group))
        .join(EveItem, EveItem.id == JitaReactionMargins.eve_item_id)
        .join(BlueprintModel, BlueprintModel.id == EveItem.blueprint_id)
        .filter(BlueprintModel.id.in_(user_bp_ids))
        .filter(JitaReactionMargins.benefit.isnot(None))
        .order_by(JitaReactionMargins.benefit.desc())
    )

    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template(
        'jita_reactions/show.html',
        rows=pagination.items,
        pagination=pagination,
    )


@bp.route('/jita_reactions/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('jita_reactions.show'))
