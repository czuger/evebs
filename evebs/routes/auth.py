import base64
import json
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from flask import Blueprint as FlaskBlueprint, abort, current_app, flash, redirect, request, session, url_for
from flask_login import login_user, logout_user

from evebs.extensions import db
from evebs.models import MarketGroup, UniverseSystem, User

bp = FlaskBlueprint('auth', __name__)

EVE_AUTH_URL  = 'https://login.eveonline.com/v2/oauth/authorize'
EVE_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'

DEFAULT_SCOPES = ' '.join([
    'esi-characters.read_orders.v1',
    'esi-assets.read_assets.v1',
    'esi-characters.read_blueprints.v1',
    'esi-industry.read_character_jobs.v1',
])


def _basic_auth_header():
    client_id  = current_app.config['ESI_CLIENT_ID']
    secret_key = current_app.config['ESI_SECRET_KEY']
    return 'Basic ' + base64.b64encode(f'{client_id}:{secret_key}'.encode()).decode()


def _jwt_payload(token):
    part = token.split('.')[1]
    part += '=' * (-len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(part))


@bp.route('/auth/eve_online_sso', methods=['GET', 'POST'])
def login():
    state  = secrets.token_hex(16)
    scopes = current_app.config.get('EVE_SSO_SCOPES', DEFAULT_SCOPES)
    params = {
        'response_type': 'code',
        'redirect_uri':  url_for('auth.callback', _external=True),
        'client_id':     current_app.config['ESI_CLIENT_ID'],
        'scope':         scopes,
        'state':         state,
    }
    session['oauth_state'] = state
    return redirect(f'{EVE_AUTH_URL}?{urlencode(params)}')


@bp.route('/auth/eve_online_sso/callback')
def callback():
    returned_state = request.args.get('state')
    expected_state = session.pop('oauth_state', None)
    if not returned_state or returned_state != expected_state:
        flash('Authentication failed: invalid state.')
        return redirect(url_for('main.index'))

    code = request.args.get('code')
    if not code:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))

    resp = requests.post(EVE_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code':       code,
    }, headers={
        'Authorization': _basic_auth_header(),
        'Content-Type':  'application/x-www-form-urlencoded',
    })
    if not resp.ok:
        flash('Token exchange failed.')
        return redirect(url_for('main.index'))

    data          = resp.json()
    access_token  = data['access_token']
    refresh_token = data.get('refresh_token')
    expires_in    = data.get('expires_in', 1200)

    claims = _jwt_payload(access_token)
    uid    = claims['sub'].split(':')[-1]
    name   = claims.get('name')

    user = User.query.filter_by(uid=uid).first()
    if not user:
        user = User(uid=uid, provider='eve_online_sso')
    user.name        = name
    user.token       = access_token
    user.renew_token = refresh_token
    user.expires_on  = datetime.utcnow() + timedelta(seconds=expires_in)
    db.session.add(user)
    db.session.flush()

    _set_defaults(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('buy_orders.show'))


@bp.route('/auth/test_login/<int:user_id>')
def test_login(user_id):
    if not current_app.config.get('TESTING'):
        abort(404)
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    login_user(user)
    return redirect(url_for('list_items.show'))


@bp.route('/signout', methods=['GET', 'POST'])
def signout():
    logout_user()
    return redirect(url_for('main.index'))


def _set_defaults(user):
    if user.initialization_finalized:
        return
    for system_id in [30000142, 30002187]:
        th = UniverseSystem.query.filter_by(id=system_id, trade_hub=True).first()
        if th and th not in user.trade_hubs:
            user.trade_hubs.append(th)
    for group_id in [973, 972, 927, 917]:
        mg = MarketGroup.query.filter_by(id=group_id).first()
        if mg:
            for item in mg.eve_items:
                if item not in user.eve_items:
                    user.eve_items.append(item)
    user.initialization_finalized = True


def renew_token(user):
    resp = requests.post(EVE_TOKEN_URL, data={
        'grant_type':    'refresh_token',
        'refresh_token': user.renew_token,
    }, headers={
        'Authorization': _basic_auth_header(),
        'Content-Type':  'application/x-www-form-urlencoded',
    })
    if resp.ok:
        data            = resp.json()
        user.token      = data['access_token']
        user.expires_on = datetime.utcnow() + timedelta(seconds=data.get('expires_in', 1200))
        db.session.commit()
