"""Guide routes: dashboard, profile, scholar fetch, and student responses."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from scholarly import scholarly

from models import db, Student, Guide, Preference, Allocation, Notification
from utils import log_action, role_required

guide_bp = Blueprint('guide', __name__, url_prefix='/guide')


@guide_bp.route('/dashboard')
@login_required
@role_required('guide')
def dashboard():
    guide = current_user.guide_profile
    allocations = Allocation.query.filter_by(guide_id=guide.id).all() if guide else []

    # Get students who listed this guide in their preferences
    applicants = []
    prefs = Preference.query.filter(
        (Preference.choice_1_id == guide.id) |
        (Preference.choice_2_id == guide.id) |
        (Preference.choice_3_id == guide.id)
    ).all()
    for pref in prefs:
        student = db.session.get(Student, pref.student_id)
        if student:
            rank = 0
            if pref.choice_1_id == guide.id:
                rank = 1
            elif pref.choice_2_id == guide.id:
                rank = 2
            elif pref.choice_3_id == guide.id:
                rank = 3
            applicants.append({
                'student': student,
                'rank': rank,
                'score': guide.applicant_score(student),
                'allocation': Allocation.query.filter_by(student_id=student.id, guide_id=guide.id).first()
            })
    applicants.sort(key=lambda x: x['score'], reverse=True)

    notifications = (Notification.query
                     .filter_by(user_id=current_user.id)
                     .order_by(Notification.created_at.desc())
                     .limit(10).all())

    return render_template('guide/dashboard.html',
                           guide=guide, allocations=allocations,
                           applicants=applicants, notifications=notifications)


@guide_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('guide')
def profile():
    guide = current_user.guide_profile

    if request.method == 'POST':
        guide.bio = request.form.get('bio', '')
        try:
            guide.capacity = int(request.form.get('capacity', 5))
        except ValueError:
            guide.capacity = 5
        guide.designation = request.form.get('designation', 'Assistant Professor')
        areas = request.form.get('research_areas_text', '')
        guide.research_areas = [a.strip() for a in areas.split(',') if a.strip()]
        db.session.commit()
        log_action('update_profile', target=str(guide.id))
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('guide.dashboard'))

    return render_template('guide/profile.html', guide=guide)


@guide_bp.route('/fetch-scholar', methods=['POST'])
@login_required
@role_required('guide')
def fetch_scholar():
    guide = current_user.guide_profile
    try:
        search_query = scholarly.search_author(current_user.name)
        author = next(search_query)
        scholarly.fill(author, sections=['publications'])

        pubs = []
        for pub in author['publications'][:5]:
            pubs.append(pub['bib'].get('title', 'Unknown Publication'))

        guide.scholar_id = author['scholar_id']
        guide.publications = pubs
        db.session.commit()
        log_action('fetch_scholar', target=str(guide.id))
        flash('Successfully fetched publications from Google Scholar!', 'success')
    except StopIteration:
        flash('Could not find profile on Google Scholar with your exact name.', 'error')
    except Exception as e:
        flash(f'Google Scholar API Error: {str(e)}', 'error')

    return redirect(url_for('guide.profile'))


@guide_bp.route('/respond', methods=['POST'])
@login_required
@role_required('guide')
def respond():
    guide = current_user.guide_profile
    try:
        student_id = int(request.form.get('student_id'))
    except (TypeError, ValueError):
        flash('Invalid student ID.', 'error')
        return redirect(url_for('guide.dashboard'))
    action = request.form.get('action')  # accept, reject, waitlist

    alloc = Allocation.query.filter_by(student_id=student_id, guide_id=guide.id).first()
    student = db.session.get(Student, student_id)

    if action == 'accept' and alloc:
        alloc.status = 'confirmed'
        notif = Notification(
            user_id=student.user_id, type='success', title='Guide Confirmed!',
            message=f'{current_user.name} has confirmed your allocation.'
        )
        db.session.add(notif)
    elif action == 'reject' and alloc:
        alloc.status = 'rejected'
        guide.current_load = max(0, guide.current_load - 1)
        notif = Notification(
            user_id=student.user_id, type='error', title='Allocation Rejected',
            message=f'{current_user.name} has rejected your allocation. Admin will reassign.'
        )
        db.session.add(notif)
    elif action == 'waitlist' and alloc:
        alloc.status = 'waitlisted'
        notif = Notification(
            user_id=student.user_id, type='warning', title='Waitlisted',
            message=f'You have been waitlisted by {current_user.name}.'
        )
        db.session.add(notif)

    db.session.commit()
    log_action('guide_response', target=str(student_id), details=f'action={action}')
    flash(f'Student {action}ed successfully.', 'success')
    return redirect(url_for('guide.dashboard'))
