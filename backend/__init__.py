from fastapi import APIRouter

from db import router as db_router

router = APIRouter()

router.include_router(db_router)

__all__ = ["router"]

