import os
import base64
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode


def _jwt_payload(token):
    """Decode the payload of an Eve SSO v2 JWT without signature verification."""
    part = token.split('.')[1]
    part += '=' * (-len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(part))

import requests
from flask import Blueprint, redirect, url_for, session, request, current_app, flash
from flask_login import login_user, logout_user

from evebs.extensions import db
from evebs.models import User, TradeHub, MarketGroup

bp = Blueprint('auth', __name__)

EVE_AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize'
EVE_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
EVE_CHAR_INFO_URL = 'https://esi.evetech.net/latest/characters/{}/'

DEFAULT_SCOPES = ' '.join([
    'esi-characters.read_orders.v1',
    'esi-assets.read_assets.v1',
    'esi-characters.read_blueprints.v1',
])


@bp.route('/auth/eve_online_sso', methods=['POST'])
def login():
    client_id = current_app.config['ESI_CLIENT_ID']
    scopes = current_app.config.get('EVE_SSO_SCOPES', DEFAULT_SCOPES)
    callback = url_for('auth.callback', _external=True)
    params = {
        'response_type': 'code',
        'redirect_uri': callback,
        'client_id': client_id,
        'scope': scopes,
        'state': os.urandom(16).hex(),
    }
    session['oauth_state'] = params['state']
    return redirect(f'{EVE_AUTH_URL}?{urlencode(params)}')


@bp.route('/auth/eve_online_sso/callback')
def callback():
    code = request.args.get('code')
    if not code:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))

    client_id = current_app.config['ESI_CLIENT_ID']
    secret_key = current_app.config['ESI_SECRET_KEY']

    auth = base64.b64encode(f'{client_id}:{secret_key}'.encode()).decode()
    resp = requests.post(EVE_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
    }, headers={'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'})

    if not resp.ok:
        flash('Token exchange failed.')
        return redirect(url_for('main.index'))

    token_data = resp.json()
    access_token = token_data['access_token']
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in', 1200)

    claims = _jwt_payload(access_token)
    # sub is "CHARACTER:EVE:<character_id>"
    uid = claims['sub'].split(':')[-1]
    name = claims.get('name')

    user = User.query.filter_by(uid=uid).first()
    if not user:
        user = User(uid=uid, provider='eve_online_sso')
    user.name = name
    user.token = access_token
    user.renew_token = refresh_token
    user.expires_on = datetime.utcnow() + timedelta(seconds=expires_in)
    db.session.add(user)
    db.session.flush()

    _set_default_package(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('buy_orders.show'))


@bp.route('/signout', methods=['GET', 'POST'])
def signout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/auth/failure')
def failure():
    flash('Authentication failed, please try again.')
    return redirect(url_for('main.index'))


def _set_default_package(user):
    if user.initialization_finalized:
        return
    for th_system_id in [30000142, 30002187]:
        th = TradeHub.query.filter_by(eve_system_id=th_system_id).first()
        if th and th not in user.trade_hubs:
            user.trade_hubs.append(th)

    for group_cpp_id in [973, 972, 927, 917]:
        mg = MarketGroup.query.filter_by(cpp_market_group_id=group_cpp_id).first()
        if mg:
            for item in mg.eve_items:
                if item not in user.eve_items:
                    user.eve_items.append(item)

    user.initialization_finalized = True


def renew_token(user):
    client_id = current_app.config['ESI_CLIENT_ID']
    secret_key = current_app.config['ESI_SECRET_KEY']
    auth = base64.b64encode(f'{client_id}:{secret_key}'.encode()).decode()
    resp = requests.post(EVE_TOKEN_URL, data={
        'grant_type': 'refresh_token',
        'refresh_token': user.renew_token,
    }, headers={'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'})
    if resp.ok:
        data = resp.json()
        user.token = data['access_token']
        user.expires_on = datetime.utcnow() + timedelta(seconds=data.get('expires_in', 1200))
        db.session.commit()
