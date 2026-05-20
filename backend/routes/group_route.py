from fastapi import APIRouter

from auth.util import AdminDep, UserDep
from db.get_db import SessionDep

from backend.schemas import GroupCreate, GroupRead, GroupUpdate
from backend.models import Group
from backend.functions import create_group, get_group, update_group, delete_group, get_groups


router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupRead)
async def create_group_route(db: SessionDep, group: GroupCreate, user: AdminDep) -> GroupRead:
    return await create_group(db, group)


@router.get("/", response_model=list[GroupRead])
async def get_groups_route(db: SessionDep, user: UserDep) -> list[GroupRead]:
    return await get_groups(db)


@router.get("/{group_id}", response_model=GroupRead)
async def get_group_route(db: SessionDep, group_id: int, user: UserDep) -> GroupRead:
    return await get_group(db, group_id)



@router.put("/{group_id}", response_model=GroupRead)
async def update_group_route(db: SessionDep, group: GroupUpdate, group_id: int, user: AdminDep) -> GroupRead:
    return await update_group(db, group, group_id)


@router.delete("/{group_id}")
async def delete_group_route(db: SessionDep, group_id: int, user: AdminDep) -> bool:
    return await delete_group(db, group_id)




