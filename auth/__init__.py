from fastapi import APIRouter

from auth.api import router as auth_router
from auth.endpoint import router as user_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
