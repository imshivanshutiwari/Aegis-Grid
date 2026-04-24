"""Tests for the matching algorithm."""

import pytest
from app import app
from models import db, User, Student, Guide, Preference, Allocation, Notification, AuditLog
from matching import run_matching


@pytest.fixture
def test_app():
    """Configure a fresh in-memory database for each test."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _create_user(role, name, email):
    import bcrypt
    hashed = bcrypt.hashpw(b'pass', bcrypt.gensalt()).decode('utf-8')
    u = User(name=name, email=email, password_hash=hashed, role=role)
    db.session.add(u)
    db.session.flush()
    return u


def _setup_scenario(test_app):
    """Create 2 guides and 3 students with preferences inside the app context."""
    with test_app.app_context():
        # Guides
        ug1 = _create_user('guide', 'Dr. Alpha', 'alpha@uni.edu')
        ug2 = _create_user('guide', 'Dr. Beta', 'beta@uni.edu')
        g1 = Guide(user_id=ug1.id, capacity=2)
        g1.research_areas = ['ML', 'CV']
        g2 = Guide(user_id=ug2.id, capacity=2)
        g2.research_areas = ['NLP', 'IR']
        db.session.add_all([g1, g2])
        db.session.flush()

        # Students
        us1 = _create_user('student', 'Alice', 'alice@uni.edu')
        us2 = _create_user('student', 'Bob', 'bob@uni.edu')
        us3 = _create_user('student', 'Carol', 'carol@uni.edu')
        s1 = Student(user_id=us1.id, cgpa=9.0)
        s1.area_of_interest = ['ML']
        s2 = Student(user_id=us2.id, cgpa=8.0)
        s2.area_of_interest = ['NLP']
        s3 = Student(user_id=us3.id, cgpa=7.0)
        s3.area_of_interest = ['CV']
        db.session.add_all([s1, s2, s3])
        db.session.flush()

        # Preferences
        p1 = Preference(student_id=s1.id, choice_1_id=g1.id, choice_2_id=g2.id)
        p2 = Preference(student_id=s2.id, choice_1_id=g2.id, choice_2_id=g1.id)
        p3 = Preference(student_id=s3.id, choice_1_id=g1.id, choice_2_id=g2.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()


class TestRunMatching:
    def test_all_students_matched(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            stats = run_matching()
            total_matched = stats['phase1_matched'] + stats['phase2_matched']
            assert total_matched == stats['total_students']
            assert stats['unmatched'] == 0

    def test_stats_keys_present(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            stats = run_matching()
            for key in ('phase1_matched', 'phase2_matched', 'unmatched', 'total_students', 'details'):
                assert key in stats

    def test_allocations_created(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            run_matching()
            student_count = Student.query.count()
            allocation_count = Allocation.query.count()
            assert allocation_count == student_count

    def test_guide_load_updated(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            run_matching()
            for guide in Guide.query.all():
                assert guide.current_load == Allocation.query.filter_by(guide_id=guide.id).count()

    def test_notifications_created(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            run_matching()
            # At least one notification per student
            student_count = Student.query.count()
            notif_count = Notification.query.count()
            assert notif_count >= student_count

    def test_audit_log_created(self, test_app):
        _setup_scenario(test_app)
        with test_app.app_context():
            run_matching()
            log = AuditLog.query.filter_by(action='matching_algorithm_run').first()
            assert log is not None

    def test_idempotent_rerun(self, test_app):
        """Running matching twice should not double-count allocations."""
        _setup_scenario(test_app)
        with test_app.app_context():
            run_matching()
            first_count = Allocation.query.count()
            run_matching()
            second_count = Allocation.query.count()
            assert first_count == second_count

    def test_no_students_no_crash(self, test_app):
        """Matching with no students should return zero stats gracefully."""
        with test_app.app_context():
            stats = run_matching()
            assert stats['total_students'] == 0
            assert stats['phase1_matched'] == 0
