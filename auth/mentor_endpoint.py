from fastapi import APIRouter
from typing import List

from backend.schemas import GroupRead
from db.get_db import SessionDep
from auth.util import MentorDep
from auth.schema import StudentRead
from auth.performance_service import get_mentor_groups, get_mentor_students

router = APIRouter()

@router.get("/my-groups", response_model=List[GroupRead])
async def get_my_groups_endpoint(current_user: MentorDep, db: SessionDep):
    return await get_mentor_groups(db, current_user['id'])

@router.get("/my-students", response_model=List[StudentRead])
async def get_my_students_endpoint(current_user: MentorDep, db: SessionDep, group_id: int = None):
    return await get_mentor_students(db, current_user['id'], group_id)
