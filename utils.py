"""
Shared utilities for the Guide Selection application.
Contains helpers used across multiple blueprints.
"""

import os
from datetime import datetime
from functools import wraps

from flask import redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename

from models import db, AuditLog


def role_required(*roles):
    """Decorator to restrict access to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_action(action, target='', details=''):
    """Helper to create an audit log entry."""
    audit = AuditLog(
        actor_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        target=target,
        details=details
    )
    db.session.add(audit)
    db.session.commit()


def send_local_email(to, subject, body):
    """Simulate sending an email by logging to a local file."""
    os.makedirs('emails', exist_ok=True)
    safe_to = secure_filename(to.replace('@', '_'))
    filename = f"emails/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_to}.txt"
    try:
        with open(filename, 'w') as f:
            f.write(f"To: {to}\nSubject: {subject}\n\n{body}")
    except Exception:
        pass
