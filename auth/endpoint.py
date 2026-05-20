from fastapi import APIRouter

from auth.model import UserRole
from db.get_db import SessionDep
from auth.schema import (
    UserRead, UserUpdateUnique, UserUpdatePassword, UserUpdateName,
    AdminCreate, AdminRead, StudentCreate, StudentRead, MentorCreate, MentorRead,
    StudentUpdate, MentorUpdate

)
from auth.util import (
    update_user_name, update_user_unique, update_user_password, get_user_by_id,
    get_users, delete_user, UserDep, get_user_by_email, get_user_by_phone,
    AdminDep, create_admin, create_student, create_mentor, get_admins, get_admin, delete_admin,
    get_students, get_student, delete_student, get_mentors, get_mentor, delete_mentor, update_mentor, update_student
)


router = APIRouter()


@router.post("/admin", response_model=AdminRead)
async def register_admin(user: AdminCreate, current_user: AdminDep, db: SessionDep):
    return await create_admin(db, user)


@router.get("/admin", response_model=list[AdminRead])
async def get_admins_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1):
    return await get_admins(db, limit=limit, page=page)


@router.get("/admin/{admin_id}", response_model=AdminRead)
async def get_admin_endpoint(admin_id: int, current_user: AdminDep, db: SessionDep):
    return await get_admin(db, admin_id)


@router.delete("/admin/{admin_id}")
async def delete_admin_endpoint(admin_id: int, current_user: AdminDep, db: SessionDep):
    return await delete_admin(db, admin_id)


@router.post("/student", response_model=StudentRead)
async def register_student(user: StudentCreate, current_user: AdminDep, db: SessionDep):
    return await create_student(db, user)


@router.get("/student", response_model=list[StudentRead])
async def get_students_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1):
    return await get_students(db, limit=limit, page=page)


@router.get("/student/{student_id}", response_model=StudentRead)
async def get_student_endpoint(student_id: int, current_user: AdminDep, db: SessionDep):
    return await get_student(db, student_id)


@router.put("/student/{student_id}")
async def update_student_endpoint(student_id: int, user: StudentUpdate, current_user: AdminDep, db: SessionDep):
    return await update_student(db, student_id, user)


@router.delete("/student/{student_id}")
async def delete_student_endpoint(student_id: int, current_user: AdminDep, db: SessionDep):
    return await delete_student(db, student_id)


@router.post("/mentor", response_model=MentorRead)
async def register_mentor(user: MentorCreate, current_user: AdminDep, db: SessionDep):
    return await create_mentor(db, user)


@router.get("/mentor", response_model=list[MentorRead])
async def get_mentors_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1):
    return await get_mentors(db, limit=limit, page=page)


@router.get("/mentor/{mentor_id}", response_model=MentorRead)
async def get_mentor_endpoint(mentor_id: int, current_user: AdminDep, db: SessionDep):
    return await get_mentor(db, mentor_id)


@router.delete("/mentor/{mentor_id}")
async def delete_mentor_endpoint(mentor_id: int, current_user: AdminDep, db: SessionDep):
    return await delete_mentor(db, mentor_id)


@router.put("/mentor/{mentor_id}")
async def update_mentor_endpoint(mentor_id: int, user: MentorUpdate, current_user: AdminDep, db: SessionDep):
    return await update_mentor(db, mentor_id, user)


@router.get("/", response_model=list[UserRead])
async def get_users_endpoint(current_user: UserDep, db: SessionDep, limit: int = 10, page: int = 1, role: UserRole = None):
    return await get_users(db, limit=limit, page=page, role=role if role else None)


@router.get('/id/{user_id}', response_model=UserRead)
async def get_user_by_id_endpoint(user_id: int, current_user: UserDep, db: SessionDep):
    return await get_user_by_id(db, user_id)


@router.get('/email/{user_email}', response_model=UserRead)
async def get_user_by_email_endpoint(email: str, current_user: AdminDep, db: SessionDep):
    return await get_user_by_email(db, email)


@router.get('/phone/{user_phone}', response_model=UserRead)
async def get_user_by_phone_endpoint(phone: str, current_user: AdminDep, db: SessionDep):
    return await get_user_by_phone(db, phone)


@router.put('/update_password/')
async def update_user_password_endpoint(user: UserUpdatePassword, current_user: UserDep, db: SessionDep):
    return await update_user_password(db, current_user['id'], user)


@router.put('/update_name/')
async def update_user_name_endpoint(user: UserUpdateName, current_user: UserDep, db: SessionDep):
    return await update_user_name(db, current_user['id'], user)


@router.put('/update_unique/', response_model=UserRead)
async def update_user_unique_endpoint(user: UserUpdateUnique, current_user: UserDep, db: SessionDep):
    return await update_user_unique(db, current_user['id'], user)


@router.delete('/{user_id}')
async def delete_user_endpoint(user_id: int, current_user: UserDep, db: SessionDep):
    return await delete_user(db, user_id)

