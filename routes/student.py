"""Student routes: dashboard and guide preferences."""

from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db, Student, Guide, Preference, Allocation, Notification
from utils import log_action, role_required

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    student = current_user.student_profile
    allocation = Allocation.query.filter_by(student_id=student.id).first() if student else None
    guide = db.session.get(Guide, allocation.guide_id) if allocation else None
    notifications = (Notification.query
                     .filter_by(user_id=current_user.id)
                     .order_by(Notification.created_at.desc())
                     .limit(10).all())
    guides = Guide.query.all()

    return render_template('student/dashboard.html',
                           student=student, allocation=allocation,
                           assigned_guide=guide, notifications=notifications,
                           guides=guides)


@student_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
@role_required('student')
def preferences():
    student = current_user.student_profile
    guides = Guide.query.all()
    existing_pref = Preference.query.filter_by(student_id=student.id).first()

    if request.method == 'POST':
        c1 = request.form.get('choice_1')
        c2 = request.form.get('choice_2')
        c3 = request.form.get('choice_3')

        # Validate no duplicates
        choices = [c for c in [c1, c2, c3] if c]
        if len(choices) != len(set(choices)):
            flash('Each preference must be a different guide.', 'error')
            return render_template('student/preferences.html',
                                   student=student, guides=guides, preference=existing_pref)

        if existing_pref:
            existing_pref.choice_1_id = int(c1) if c1 else None
            existing_pref.choice_2_id = int(c2) if c2 else None
            existing_pref.choice_3_id = int(c3) if c3 else None
            existing_pref.submitted_at = datetime.now(timezone.utc)
        else:
            pref = Preference(
                student_id=student.id,
                choice_1_id=int(c1) if c1 else None,
                choice_2_id=int(c2) if c2 else None,
                choice_3_id=int(c3) if c3 else None
            )
            db.session.add(pref)

        notif = Notification(
            user_id=current_user.id, type='success', title='Preferences Saved',
            message='Your guide preferences have been submitted successfully.'
        )
        db.session.add(notif)
        db.session.commit()
        log_action('submit_preferences', target=str(student.id), details=f'choices={choices}')
        flash('Preferences submitted successfully!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/preferences.html',
                           student=student, guides=guides, preference=existing_pref)
