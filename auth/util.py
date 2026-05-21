from datetime import timedelta
from typing import Annotated, List

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from auth.model import User, TokenBlacklist, Admin, Student, Mentor, UserRole, MonthlyScore, Certificate, CertificateStatus
from auth.schema import (
    TokenData,
    UserRead,
    UserUpdateUnique,
    UserUpdatePassword,
    UserUpdateName,
    AdminCreate,
    AdminRead,
    StudentCreate,
    StudentRead,
    StudentUpdate,
    MentorCreate,
    MentorRead,
    MentorUpdate,
    MonthlyScoreCreate,
    MonthlyScoreRead,
    CertificateRead,
    CertificateUpdateStatus, MonthlyScoreUpdate,
)
from backend.models.group_model import Group
from config import SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from db.get_db import SessionDep
from db.orm_loads import admin_read_load_options, mentor_read_load_options, student_read_load_options
from config import now_tashkent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



async def blacklist_token(token: str, db: AsyncSession):
    try:
        token_blacklist = TokenBlacklist(jti=token)
        db.add(token_blacklist)
        await db.commit()
        await db.refresh(token_blacklist)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def is_token_blacklisted(token: str, db: AsyncSession) -> bool:
    try:
        res = await db.execute(select(TokenBlacklist).filter_by(jti=token))
        token_blacklist = res.scalars().first()
        if token_blacklist:
            return True
        return False
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user_by_phone(db: AsyncSession, phone: str) -> UserRead:
    res = await db.execute(select(User).filter_by(phone=phone))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this phone number not found")
    return UserRead.model_validate(user)


async def get_user_by_phone_with_pass(db: AsyncSession, phone: str) -> User:
    res = await db.execute(select(User).filter_by(phone=phone))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this phone number not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> UserRead:
    res = await db.execute(select(User).filter_by(email=email))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")
    return UserRead.model_validate(user)


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
    res = await db.execute(select(User).filter_by(id=user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)


async def get_user_by_id_with_pass(db: AsyncSession, user_id: int) -> User:
    res = await db.execute(select(User).filter_by(id=user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def authenticate_user(db: AsyncSession, phone: str, password: str):
    user = await get_user_by_phone_with_pass(db, phone)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = now_tashkent() + expires_delta
    else:
        expire = now_tashkent() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: SessionDep,
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    is_t_black = await is_token_blacklisted(token, db)
    if is_t_black:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        phone: str = payload.get("phone")
        email: str = payload.get("email")
        if phone is None:
            raise credentials_exception
        token_data = TokenData(phone=phone)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_phone_with_pass(db, phone=token_data.phone)
    if user is None:
        raise credentials_exception
    return {"id": user_id, "role": role, "phone": phone, "email": email}


UserDep = Annotated[dict, Depends(get_current_user)]


async def create_admin(db: AsyncSession, admin_in: AdminCreate) -> AdminRead:
    try:
        hashed_password = get_password_hash(admin_in.password)
        user_obj = User(
            hashed_password=hashed_password,
            phone=admin_in.phone,
            email=admin_in.email,
            first_name=admin_in.first_name,
            last_name=admin_in.last_name,
            father_name=admin_in.father_name,
            role=UserRole.ADMIN,
        )
        db.add(user_obj)
        await db.flush()

        admin_obj = Admin(user_id=user_obj.id, is_superadmin=admin_in.is_superadmin)
        db.add(admin_obj)

        await db.commit()
        return await get_admin(db, user_obj.id)
    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'unique' in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this phone or email already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_admin(db: AsyncSession, admin_id: int) -> AdminRead:
    res = await db.execute(
        select(Admin)
        .options(*admin_read_load_options())
        .filter_by(user_id=admin_id)
    )
    admin = res.scalars().first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return AdminRead.model_validate(admin)


async def get_admins(db: AsyncSession, limit: int = 10, page: int = 1) -> list[AdminRead]:
    res = await db.execute(
        select(Admin)
        .options(*admin_read_load_options())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    admins = res.scalars().all()
    return [AdminRead.model_validate(admin) for admin in admins]


async def delete_admin(db: AsyncSession, admin_id: int):
    res = await db.execute(select(Admin).filter_by(user_id=admin_id))
    admin = res.scalars().first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    user = await get_user_by_id_with_pass(db, admin.user_id)
    try:
        await db.delete(admin)
        await db.delete(user)
        await db.commit()
        return {"detail": "Admin and user deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def create_student(db: AsyncSession, student_in: StudentCreate) -> StudentRead:
    try:
        hashed_password = get_password_hash(student_in.password)
        user_obj = User(
            hashed_password=hashed_password,
            phone=student_in.phone,
            email=student_in.email,
            first_name=student_in.first_name,
            last_name=student_in.last_name,
            father_name=student_in.father_name,
            role=UserRole.STUDENT,
        )
        db.add(user_obj)
        await db.flush()

        student_obj = Student(
            user_id=user_obj.id,
            student_id=student_in.student_id,
            group_id=student_in.group_id,
            is_grant=student_in.is_grant,
            course_number=student_in.course_number,
            attendance=student_in.attendance,
            academic=student_in.academic,
            assignment=student_in.assignment,
        )
        db.add(student_obj)
        await db.commit()
        return await get_student(db, user_obj.id)
    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'unique' in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conflict: unique constraint violated")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_student(db: AsyncSession, student_id: int) -> StudentRead:
    res = await db.execute(
        select(Student)
        .options(*student_read_load_options())
        .filter_by(user_id=student_id)
    )
    student = res.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentRead.model_validate(student)


async def get_students(db: AsyncSession, limit: int = 10, page: int = 1) -> list[StudentRead]:
    res = await db.execute(
        select(Student)
        .options(*student_read_load_options())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    students = res.scalars().all()
    return [StudentRead.model_validate(student) for student in students]


async def update_student(db: AsyncSession, student_id: int, student_in: StudentUpdate) -> StudentRead:
    res = await db.execute(select(Student).filter_by(user_id=student_id))
    student = res.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    user = await get_user_by_id_with_pass(db, student.user_id)
    try:
        # update user fields
        data = student_in.model_dump(exclude_unset=True)
        user_fields = {k: v for k, v in data.items() if k in ('phone','email','first_name','last_name','father_name','password')}
        for k,v in user_fields.items():
            if k == 'password':
                setattr(user, 'hashed_password', get_password_hash(v))
            else:
                setattr(user, k, v)

        # update student fields
        student_fields = {k: v for k, v in data.items() if k not in user_fields}
        for k, v in student_fields.items():
            setattr(student, k, v)

        db.add(user)
        db.add(student)
        await db.commit()
        return await get_student(db, student_id)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_student(db: AsyncSession, student_id: int):
    res = await db.execute(select(Student).filter_by(user_id=student_id))
    student = res.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    user = await get_user_by_id_with_pass(db, student.user_id)
    try:
        await db.delete(student)
        await db.delete(user)
        await db.commit()
        return {"detail": "Student and user deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def create_mentor(db: AsyncSession, mentor_in: MentorCreate) -> MentorRead:
    try:
        hashed_password = get_password_hash(mentor_in.password)
        user_obj = User(
            hashed_password=hashed_password,
            phone=mentor_in.phone,
            email=mentor_in.email,
            first_name=mentor_in.first_name,
            last_name=mentor_in.last_name,
            father_name=mentor_in.father_name,
            role=UserRole.MENTOR,
        )
        db.add(user_obj)
        await db.flush()

        mentor_obj = Mentor(user_id=user_obj.id)
        db.add(mentor_obj)
        await db.flush()

        # assign groups if provided
        if mentor_in.group_ids:
            for gid in mentor_in.group_ids:
                gres = await db.execute(select(Group).filter_by(id=gid))
                g = gres.scalars().first()
                if g:
                    g.mentor_id = mentor_obj.user_id
                    db.add(g)

        await db.commit()
        return await get_mentor(db, mentor_obj.user_id)
    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'unique' in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conflict: unique constraint violated")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_mentor(db: AsyncSession, user_id: int) -> MentorRead:
    res = await db.execute(
        select(Mentor)
        .options(*mentor_read_load_options())
        .filter_by(user_id=user_id)
    )
    mentor = res.scalars().first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return MentorRead.model_validate(mentor)


async def update_mentor(db: AsyncSession, user_id: int, mentor_in: MentorUpdate) -> MentorRead:
    res = await db.execute(select(Mentor).filter_by(user_id=user_id))
    mentor = res.scalars().first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    user = await get_user_by_id_with_pass(db, mentor.user_id)
    try:
        data = mentor_in.model_dump(exclude_unset=True)
        user_fields = {k: v for k, v in data.items() if k in ('phone','email','first_name','last_name','father_name','password')}
        for k, v in user_fields.items():
            if k == 'password':
                setattr(user, 'hashed_password', get_password_hash(v))
            else:
                setattr(user, k, v)

        # groups
        if 'group_ids' in data and data['group_ids'] is not None:
            # clear previous groups for this mentor
            gres = await db.execute(select(Group).where(Group.mentor_id == mentor.user_id))
            prev_groups = gres.scalars().all()
            for pg in prev_groups:
                setattr(pg, 'mentor_id', None)
                db.add(pg)
            # assign new
            for gid in data['group_ids']:
                gres = await db.execute(select(Group).filter_by(id=gid))
                g = gres.scalars().first()
                if g:
                    setattr(g, 'mentor_id', mentor.user_id)
                    db.add(g)

        db.add(user)
        db.add(mentor)
        await db.commit()
        return await get_mentor(db, user_id)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_mentor(db: AsyncSession, user_id: int):
    res = await db.execute(select(Mentor).filter_by(user_id=user_id))
    mentor = res.scalars().first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    user = await get_user_by_id_with_pass(db, mentor.user_id)
    try:
        # unassign groups
        gres = await db.execute(select(Group).where(Group.mentor_id == mentor.user_id))
        groups = gres.scalars().all()
        for g in groups:
            setattr(g, 'mentor_id', None)
            db.add(g)

        await db.delete(mentor)
        await db.delete(user)
        await db.commit()
        return {"detail": "Mentor and user deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_mentors(db: AsyncSession, limit: int = 10, page: int = 1) -> list[MentorRead]:
    stmt = (
        select(Mentor)
        .options(*mentor_read_load_options())
        .limit(limit)
        .offset((page - 1) * limit)
    )
    res = await db.execute(stmt)
    mentors = res.scalars().all()
    return [MentorRead.model_validate(m) for m in mentors] or []


async def get_users(db: AsyncSession, limit: int = 10, page: int = 1, role: str = None) -> list[UserRead]:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.limit(limit).offset((page - 1) * limit)
    res = await db.execute(stmt)
    users = res.scalars().all()
    return [UserRead.model_validate(user) for user in users] or []


async def update_user_password(db: AsyncSession, user_id: int, user: UserUpdatePassword):
    user_db = await get_user_by_id_with_pass(db, user_id)
    if verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='New password cannot be the same as the old password')

    try:
        hashed_pass = get_password_hash(user.password)
        user_db.hashed_password = hashed_pass
        db.add(user_db)
        await db.commit()
        return {"detail": "Password updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update_user_name(db: AsyncSession, user_id: int, user: UserUpdateName):
    user_db = await get_user_by_id_with_pass(db, user_id)
    try:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, key, value)

        db.add(user_db)
        await db.commit()
        return {"detail": "User name updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update_user_unique(db: AsyncSession, user_id: int, user: UserUpdateUnique) -> UserRead:
    for field, value in [("phone", user.phone), ("email", user.email)]:
        if value is None:
            continue
        result = await db.execute(select(User).where(getattr(User, field).__eq__(value)))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail=f"User with this {field} already exists")

    user_db = await get_user_by_id_with_pass(db, user_id)
    try:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, key, value)

        db.add(user_db)
        await db.commit()
        return UserRead.model_validate(user_db)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id_with_pass(db, user_id)
    try:
        await db.delete(user)
        await db.commit()
        return {"detail": "User deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def read_me(db: AsyncSession, current_user) -> UserRead:
    return await get_user_by_id(db, current_user['id'])


def role_required(*allowed_roles: str):
    async def _role_checker(current_user: UserDep):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Requires role: {allowed_roles}"
            )
        return current_user
    return Depends(_role_checker)

AdminDep = Annotated[dict, role_required("admin")]
MentorDep = Annotated[dict, role_required("mentor", "admin")]
StudentDep = Annotated[dict, role_required("student", "admin")]
