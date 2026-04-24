"""Authentication routes: login, register, logout."""

import os
import random

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
from werkzeug.utils import secure_filename
import PyPDF2

from models import db, User, Student, Guide, Notification
from utils import log_action, send_local_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            log_action('login', target=user.email)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        from flask import current_app
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        department = request.form.get('department', 'Computer Science')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        colors = ['#6C63FF', '#FF6584', '#43E97B', '#F7971E', '#00C9FF', '#FC5C7D']
        user = User(
            name=name, email=email, password_hash=hashed,
            role=role, department=department,
            avatar_color=random.choice(colors)
        )
        db.session.add(user)
        db.session.flush()

        if role == 'student':
            try:
                cgpa = float(request.form.get('cgpa', 0))
            except ValueError:
                cgpa = 0.0
            interests = request.form.getlist('interests')

            # Handle SOP PDF Upload
            sop_file = request.files.get('sop_file')
            sop_path = ''
            sop_score = 0.0

            if sop_file and sop_file.filename.endswith('.pdf'):
                filename = secure_filename(f"{user.id}_{sop_file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                sop_file.save(filepath)
                sop_path = f"uploads/sops/{filename}"

                # Basic NLP Score
                try:
                    with open(filepath, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()]).lower()
                        for interest in interests:
                            if interest.lower() in text:
                                sop_score += 5.0
                except Exception as e:
                    print("PDF Error:", e)

            student = Student(user_id=user.id, cgpa=cgpa, area_of_interest=interests,
                              sop_url=sop_path, sop_score=sop_score)
            db.session.add(student)
        elif role == 'guide':
            areas = request.form.getlist('research_areas')
            try:
                capacity = int(request.form.get('capacity', 5))
            except ValueError:
                capacity = 5
            guide = Guide(user_id=user.id, research_areas=areas, capacity=capacity)
            db.session.add(guide)

        # Welcome notification
        notif = Notification(
            user_id=user.id, type='success', title='Welcome!',
            message=f'Welcome to the Guide Selection System, {name}!'
        )
        db.session.add(notif)
        db.session.commit()
        log_action('register', target=email, details=f'role={role}')

        send_local_email(email, "Welcome to GuideSelect!", f"Hello {name},\nWelcome to the platform!")

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action('logout', target=current_user.email)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
