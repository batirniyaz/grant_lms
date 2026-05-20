from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
import datetime

from db.base import Base
from config import now_tashkent

if TYPE_CHECKING:
    from auth.model import Student, Mentor


class Group(Base):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_number: Mapped[str] = mapped_column(String(length=25), unique=True)
    
    # many-to-one: many groups can have one mentor
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey('mentor.user_id'), nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)

    # one-to-many: one group has many students
    students: Mapped[List["Student"]] = relationship(back_populates="group", lazy="selectin")
    
    # many-to-one: many groups have one mentor
    mentor: Mapped["Mentor"] = relationship(back_populates="groups", lazy="selectin")
