from fastapi import APIRouter

from db import router as db_router

# We move route imports inside the function to break circular dependencies
# with auth.util -> auth.schema -> backend.schemas -> backend.__init__

def get_main_router():
    from auth import router as auth_router
    from backend.routes.group_route import router as group_router
    from backend.routes.leaderboard_route import router as leaderboard_router
    
    router = APIRouter()
    router.include_router(db_router)
    router.include_router(auth_router)
    router.include_router(group_router)
    router.include_router(leaderboard_router)
    return router

__all__ = ["get_main_router"]
