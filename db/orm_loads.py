"""Shared SQLAlchemy eager-load options for Pydantic read schemas (GroupRead, StudentRead, MentorRead)."""

from sqlalchemy.orm import joinedload, selectinload

from auth.model import Admin, Mentor, Student
from backend.models.group_model import Group


def admin_read_load_options():
    """Eager load for AdminRead (flatten_user needs Admin.user)."""
    return (joinedload(Admin.user),)


def student_read_load_options():
    """Eager load for StudentRead (user, monthly_scores, certificates)."""
    return (
        joinedload(Student.user),
        selectinload(Student.monthly_scores),
        selectinload(Student.certificates),
    )


def group_students_read_options():
    """Student tree required by StudentRead inside GroupRead (no async lazy-load)."""
    return (
        selectinload(Group.students).joinedload(Student.user),
        selectinload(Group.students).selectinload(Student.monthly_scores),
        selectinload(Group.students).selectinload(Student.certificates),
    )


def group_read_load_options():
    """Full eager load for GET /groups/ and GroupRead validation."""
    return (
        joinedload(Group.mentor).joinedload(Mentor.user),
        *group_students_read_options(),
    )


def mentor_read_load_options():
    """Full eager load for GET /user/mentor and MentorRead validation."""
    return (
        joinedload(Mentor.user),
        selectinload(Mentor.groups).options(*group_students_read_options()),
    )
