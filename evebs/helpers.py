from datetime import datetime
from flask import request
from markupsafe import Markup


def register(app):
    """Register Jinja2 globals and filters for the app."""
    app.jinja_env.globals.update(
        current_page=_current_page,
        print_isk=print_isk,
        print_pcent=print_pcent,
        print_volume=print_volume,
        safe_multiply=safe_multiply,
        show_last_update=show_last_update,
        meta_title=meta_title,
    )
    app.jinja_env.filters['isk'] = print_isk
    app.jinja_env.filters['pcent'] = print_pcent
    app.jinja_env.filters['vol'] = print_volume


def _current_page(path):
    """Return True if the current request path matches the given path."""
    return request.path == path


AMOUNTS = [
    (1e9, 'B'),
    (1e6, 'M'),
    (1e3, 'K'),
]


def _to_small_number(amount):
    """Format a number as a compact string (e.g. 1.23B, 45.6M, 789K)."""
    if amount is None:
        return 'N/A'
    if amount == float('inf'):
        return 'N/A'
    for threshold, unit in AMOUNTS:
        if abs(amount) >= threshold:
            scaled = amount / threshold
            if abs(scaled) < 10:
                return f'{scaled:.2f}{unit}'
            elif abs(scaled) < 100:
                return f'{scaled:.1f}{unit}'
            else:
                return f'{scaled:.0f}{unit}'
    if abs(amount) < 10:
        return f'{amount:.2f}'
    elif abs(amount) < 100:
        return f'{amount:.1f}'
    return f'{amount:.0f}'


def print_isk(amount):
    """Format an ISK amount as a compact string."""
    if amount is None or amount == float('inf'):
        return 'N/A'
    return _to_small_number(amount)


def print_pcent(amount, multiply=True):
    """Format a fraction as a percentage string, multiplying by 100 by default."""
    if amount is None:
        return 'N/A'
    val = amount * 100.0 if multiply else amount
    return f'{val:.2f} %'


def print_volume(amount):
    """Format a volume as a compact string."""
    if amount is None:
        return 'N/A'
    return _to_small_number(amount)


def safe_multiply(a, b):
    """Multiply two values, returning infinity if either is None."""
    if a is None or b is None:
        return float('inf')
    return a * b


def show_last_update(update_type):
    """Return a human-readable 'Last update: ...' string for the given process type."""
    from evebs.models import LastUpdate
    record = LastUpdate.query.filter_by(update_type=str(update_type)).first()
    if not record:
        return ''
    last_update = record.updated_at
    now = datetime.utcnow()
    today = now.date()
    diff_days = (today - last_update.date()).days
    if diff_days == 0:
        date_str = f'today at {last_update.hour}'
    elif diff_days == 1:
        date_str = f'yesterday at {last_update.hour}'
    else:
        date_str = f'{diff_days} days ago at {last_update.hour}'
    return f'Last update: {date_str} UTC'


def meta_title(title=None):
    """Build the full page title string with the EVE branding suffix."""
    base = title or 'EveBusinessServer (Beta)'
    return f'{base} - EVE Online market information'
