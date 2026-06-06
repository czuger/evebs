from itertools import groupby

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import Blueprint as BpModel, EveItem, MarketGroup, BpcAsset

bp = Blueprint('user_blueprints', __name__)


@bp.route('/user_blueprints')
@login_required
def show():
    user = current_user

    blueprints = (
        db.session.query(BpModel)
        .join(BpModel.users).filter_by(id=user.id)
        .join(BpModel.eve_item)
        .outerjoin(EveItem.market_group)
        .order_by(MarketGroup.name.nullslast(), BpModel.name)
        .all()
    )

    grouped = []
    for group_name, bps in groupby(
        blueprints,
        key=lambda b: b.eve_item.market_group.name
                      if b.eve_item and b.eve_item.market_group else 'Other',
    ):
        grouped.append((group_name, list(bps)))

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
                           grouped=grouped,
                           total=len(blueprints),
                           invention_rows=invention_rows,
                           default_hub=default_hub)


@bp.route('/user_blueprints/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('user_blueprints.show'))
