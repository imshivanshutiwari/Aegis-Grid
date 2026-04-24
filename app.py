"""
Guide Selection Project — Main Flask Application.
Full-stack web app for student-guide allocation.
"""

import os
from datetime import datetime, timezone

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail

from models import db, User, Notification

# ─── App Configuration ──────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'guide-selection-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///guide_selection.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'sops')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max limit

# Mail Config
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@college.edu'
app.config['MAIL_SUPPRESS_SEND'] = True
mail = Mail(app)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─── Register Blueprints ────────────────────────────────────────
from routes import auth_bp, student_bp, guide_bp, admin_bp, notifications_bp  # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notifications_bp)


# ─── Dashboard Router ───────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return redirect(url_for('student.dashboard'))
    elif current_user.role == 'guide':
        return redirect(url_for('guide.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))


# ─── Context Processors ─────────────────────────────────────────
@app.context_processor
def inject_globals():
    unread_count = 0
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
    return {'unread_count': unread_count, 'now': datetime.now(timezone.utc)}


# ─── Error Handlers ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied'), 403


# ─── Run ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
