"""Notification routes: mark individual and all notifications as read."""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from models import db, Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_read(notif_id):
    notif = db.session.get(Notification, notif_id)
    if notif and notif.user_id == current_user.id:
        notif.read = True
        db.session.commit()
    return jsonify({'status': 'ok'})


@notifications_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})
