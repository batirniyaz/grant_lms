from fastapi import APIRouter

from db import router as db_router
from auth import router as auth_router
from backend.routes.group_route import router as group_router

router = APIRouter()

router.include_router(db_router)
router.include_router(auth_router)
router.include_router(group_router)

__all__ = ["router"]

