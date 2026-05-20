
from backend.models import Group
from backend.schemas import GroupCreate, GroupRead, GroupUpdate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from db.orm_loads import group_read_load_options


async def create_group(db: AsyncSession, group: GroupCreate) -> GroupRead:
    try:
        group_obj = Group(**group.model_dump())
        db.add(group_obj)
        await db.commit()
        await db.refresh(group_obj)
        return await get_group(db, group_obj.id)
    except IntegrityError as e:
        await db.rollback()
        detail = str(e.orig) if hasattr(e, 'orig') else str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_group(db: AsyncSession, group_id: int) -> GroupRead:
    res = await db.execute(
        select(Group)
        .options(*group_read_load_options())
        .filter_by(id=group_id)
    )
    group = res.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupRead.model_validate(group)


async def get_groups(db: AsyncSession, limit: int = 10, page = 1) -> list[GroupRead]:
    res = await db.execute(
        select(Group)
        .options(*group_read_load_options())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    groups = res.scalars().all()
    return [GroupRead.model_validate(group) for group in groups]


async def update_group(db: AsyncSession, group: GroupUpdate, group_id: int) -> GroupRead:
    res = await db.execute(select(Group).filter_by(id=group_id))
    group_obj = res.scalars().first()
    if not group_obj:
        raise HTTPException(status_code=404, detail="Group not found")

    data = group.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(group_obj, key, value)

    try:
        await db.commit()
        await db.refresh(group_obj)
        return await get_group(db, group_obj.id)
    except IntegrityError as e:
        await db.rollback()
        detail = str(e.orig) if hasattr(e, 'orig') else str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_group(db: AsyncSession, group_id: int):
    res = await db.execute(select(Group).filter_by(id=group_id))
    group_obj = res.scalars().first()
    if not group_obj:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        await db.delete(group_obj)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
