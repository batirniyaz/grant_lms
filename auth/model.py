from enum import Enum as enum_Enum
from typing import Optional, List, TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, Enum as sql_Enum, Boolean

import datetime

from db.base import Base
from config import now_tashkent

if TYPE_CHECKING:
    from backend.models.group_model import Group



class UserRole(enum_Enum):
    STUDENT = 'student'
    ADMIN = 'admin'
    MENTOR = 'mentor'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(length=13), unique=True)
    email: Mapped[str | EmailStr] = mapped_column(String(length=50), unique=True)
    first_name: Mapped[str] = mapped_column(String(length=25))
    last_name: Mapped[str] = mapped_column(String(length=25))
    father_name: Mapped[str] = mapped_column(String(length=25))
    hashed_password: Mapped[str] = mapped_column(String(length=255))

    role: Mapped[UserRole] = mapped_column(sql_Enum(UserRole))
    

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)

    admin: Mapped[Optional["Admin"]] = relationship("Admin", back_populates="user", uselist=False)
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    mentor: Mapped[Optional["Mentor"]] = relationship("Mentor", back_populates="user", uselist=False)

class Admin(Base):
    __tablename__ = 'admin'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="admin")
    
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)
    

class Student(Base):
    __tablename__ = 'student'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, unique=True)

    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('group.id'), nullable=True)
    is_grant: Mapped[bool] = mapped_column(Boolean, default=False)
    course_number: Mapped[int] = mapped_column(Integer, default=1)
    attendance: Mapped[int] = mapped_column(Integer, default=0)
    academic: Mapped[int] = mapped_column(Integer, default=0)
    assignment: Mapped[int] = mapped_column(Integer, default=0)


    user: Mapped["User"] = relationship("User", back_populates="student")
    group: Mapped["Group"] = relationship("Group", back_populates="students")
    
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)
    
    
class Mentor(Base):
    __tablename__ = 'mentor'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="mentor")

    groups: Mapped[List["Group"]] = relationship(back_populates="mentor", lazy="selectin")
    
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)



class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    jti: Mapped[str] = mapped_column(String(length=255), unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)