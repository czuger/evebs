from flask import Blueprint as FlaskBlueprint, render_template
from evebs.models import MarketGroup

bp = FlaskBlueprint('market_groups', __name__)


@bp.route('/market_groups')
def index():
    groups = MarketGroup.roots().all()
    return render_template('market_groups/index.html',
                           title='Market groups',
                           groups=groups)
