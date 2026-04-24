"""Tests for database models."""

import json
import pytest
from app import app
from models import db, User, Student, Guide, Preference, Allocation, Notification, AuditLog


@pytest.fixture
def test_app():
    """Configure a fresh in-memory database for each test."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


def _make_user(role='student', email='test@example.com', name='Test User'):
    import bcrypt
    hashed = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode('utf-8')
    return User(name=name, email=email, password_hash=hashed, role=role)


# ─── User model ──────────────────────────────────────────────────

class TestUserModel:
    def test_user_repr(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.commit()
            assert 'Test User' in repr(user)
            assert 'student' in repr(user)

    def test_user_defaults(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.commit()
            assert user.is_active is True
            assert user.department == 'Computer Science'

    def test_unique_email_constraint(self, test_app):
        from sqlalchemy.exc import IntegrityError
        with test_app.app_context():
            u1 = _make_user(email='dup@example.com')
            u2 = _make_user(email='dup@example.com', name='Other')
            db.session.add(u1)
            db.session.commit()
            db.session.add(u2)
            with pytest.raises(IntegrityError):
                db.session.commit()


# ─── Student model ───────────────────────────────────────────────

class TestStudentModel:
    def test_area_of_interest_roundtrip(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, cgpa=8.5)
            student.area_of_interest = ['ML', 'NLP']
            db.session.add(student)
            db.session.commit()
            fetched = db.session.get(Student, student.id)
            assert fetched.area_of_interest == ['ML', 'NLP']

    def test_area_of_interest_invalid_json(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, cgpa=7.0)
            student._area_of_interest = 'not-valid-json'
            db.session.add(student)
            db.session.commit()
            assert student.area_of_interest == []

    def test_priority_score_cgpa_weight(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, cgpa=9.0, sop_score=5.0)
            db.session.add(student)
            db.session.commit()
            # CGPA * 10 + sop_score = 90 + 5 = 95
            assert student.priority_score == 95.0

    def test_student_repr(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, cgpa=8.0)
            db.session.add(student)
            db.session.commit()
            assert 'Test User' in repr(student)
            assert '8.0' in repr(student)


# ─── Guide model ────────────────────────────────────────────────

class TestGuideModel:
    def _make_guide(self, test_app, name='Dr. Smith', capacity=3):
        with test_app.app_context():
            user = _make_user(role='guide', email=f'{name}@uni.edu', name=name)
            db.session.add(user)
            db.session.flush()
            guide = Guide(user_id=user.id, capacity=capacity)
            guide.research_areas = ['ML', 'CV']
            db.session.add(guide)
            db.session.commit()
            return guide.id

    def test_available_slots(self, test_app):
        with test_app.app_context():
            guide_id = self._make_guide(test_app)
            guide = db.session.get(Guide, guide_id)
            assert guide.available_slots == guide.capacity

    def test_is_full(self, test_app):
        with test_app.app_context():
            guide_id = self._make_guide(test_app, capacity=1)
            guide = db.session.get(Guide, guide_id)
            assert not guide.is_full
            guide.current_load = 1
            assert guide.is_full

    def test_research_areas_roundtrip(self, test_app):
        with test_app.app_context():
            guide_id = self._make_guide(test_app)
            guide = db.session.get(Guide, guide_id)
            assert guide.research_areas == ['ML', 'CV']

    def test_research_areas_invalid_json(self, test_app):
        with test_app.app_context():
            guide_id = self._make_guide(test_app)
            guide = db.session.get(Guide, guide_id)
            guide._research_areas = 'bad-json'
            assert guide.research_areas == []


# ─── Preference model ────────────────────────────────────────────

class TestPreferenceModel:
    def test_choices_property(self, test_app):
        with test_app.app_context():
            pref = Preference(student_id=1, choice_1_id=10, choice_2_id=None, choice_3_id=20)
            assert pref.choices == [10, 20]

    def test_choices_all_none(self, test_app):
        with test_app.app_context():
            pref = Preference(student_id=1)
            assert pref.choices == []


# ─── Notification model ──────────────────────────────────────────

class TestNotificationModel:
    def test_time_ago_just_now(self, test_app):
        with test_app.app_context():
            from datetime import datetime, timezone
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            notif = Notification(
                user_id=user.id,
                message='Test',
                created_at=datetime.now(timezone.utc)
            )
            assert notif.time_ago() == 'just now'

    def test_notification_repr(self, test_app):
        with test_app.app_context():
            user = _make_user()
            db.session.add(user)
            db.session.flush()
            notif = Notification(user_id=user.id, title='Hello', message='World')
            db.session.add(notif)
            db.session.commit()
            assert 'Hello' in repr(notif)
