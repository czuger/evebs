"""Sales details: the individual recorded sales (sales_finals) for a single item."""
from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required

from config import PER_PAGE
from evebs.models import EveItem, SalesFinal
from evebs.utils import SimplePagination

bp = FlaskBlueprint('sales_details', __name__)


@bp.route('/sales_details/<int:item_id>')
@login_required
def show(item_id):
    item = EveItem.query.get_or_404(item_id)
    page = request.args.get('page', 1, type=int)

    base = SalesFinal.query.filter_by(eve_item_id=item_id)
    total = base.count()
    rows = (base.order_by(SalesFinal.day.desc(), SalesFinal.id.desc())
            .limit(PER_PAGE).offset((page - 1) * PER_PAGE).all())
    pagination = SimplePagination(page, PER_PAGE, total) if total else None

    return render_template('sales_details/show.html',
                           item=item, rows=rows, pagination=pagination, total=total,
                           title=f'Sales details for {item.name}')
