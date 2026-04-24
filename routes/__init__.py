"""Route blueprints for the Guide Selection application."""
from .auth import auth_bp
from .student import student_bp
from .guide import guide_bp
from .admin import admin_bp
from .notifications import notifications_bp

__all__ = ['auth_bp', 'student_bp', 'guide_bp', 'admin_bp', 'notifications_bp']
