from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from config import PER_PAGE
from evebs.extensions import db
from evebs.models import Blueprint as BpModel, EveItem, MarketGroup, BpcAsset
from evebs.utils import SimplePagination

bp = Blueprint('user_blueprints', __name__)


@bp.route('/user_blueprints')
@login_required
def show():
    user = current_user
    page = request.args.get('page', 1, type=int)

    base_q = (
        db.session.query(BpModel)
        .join(BpModel.users).filter_by(id=user.id)
        .join(BpModel.eve_item)
        .outerjoin(EveItem.market_group)
        .order_by(MarketGroup.name.nullslast(), BpModel.name)
    )
    total = base_q.count()
    blueprints = base_q.limit(PER_PAGE).offset((page - 1) * PER_PAGE).all()
    pagination = SimplePagination(page, PER_PAGE, total)

    invented_from_map = {}
    if blueprints:
        from esi.download_my_blueprints import _load_blueprint_activities
        activities, _ = _load_blueprint_activities()
        t2_to_t1 = {
            t2_id: t1_id
            for t1_id, acts in activities.items()
            for t2_id in acts.get('invention_products', [])
        }
        t1_ids = {t2_to_t1[bp_obj.id] for bp_obj in blueprints if bp_obj.id in t2_to_t1}
        if t1_ids:
            t1_bps = {b.id: b for b in BpModel.query.filter(BpModel.id.in_(t1_ids)).all()}
            invented_from_map = {
                bp_obj.id: t1_bps[t2_to_t1[bp_obj.id]]
                for bp_obj in blueprints
                if bp_obj.id in t2_to_t1 and t2_to_t1[bp_obj.id] in t1_bps
            }

    invention_rows = (
        db.session.query(BpModel, EveItem)
        .join(EveItem, EveItem.blueprint_id == BpModel.id)
        .join(BpcAsset, BpcAsset.eve_item_id == EveItem.id)
        .filter(
            BpcAsset.user_id == user.id,
            BpcAsset.is_potential == True,
            BpcAsset.potential_type.in_(['invent', 'copy_invent']),
        )
        .order_by(BpModel.name)
        .all()
    )

    default_hub = user.trade_hubs[0] if user.trade_hubs else None

    return render_template('user_blueprints/show.html',
                           blueprints=blueprints,
                           total=total,
                           pagination=pagination,
                           invented_from_map=invented_from_map,
                           invention_rows=invention_rows,
                           default_hub=default_hub)


@bp.route('/user_blueprints/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('user_blueprints.show'))
