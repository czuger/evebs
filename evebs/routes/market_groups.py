from flask import Blueprint, render_template
from evebs.models import MarketGroup

bp = Blueprint('market_groups', __name__)


@bp.route('/market_groups')
def index():
    """Render the root market group list."""
    groups = MarketGroup.roots().all()
    return render_template('market_groups/index.html',
                           title='Market groups',
                           groups=groups)
