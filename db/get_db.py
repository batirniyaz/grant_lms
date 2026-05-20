from typing import AsyncGenerator, Annotated

from contextlib import asynccontextmanager
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@asynccontextmanager
async def session_context() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SessionCtx = session_context
