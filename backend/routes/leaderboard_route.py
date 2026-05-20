
from fastapi import APIRouter, Depends
from typing import List

from db.get_db import SessionDep
from auth.util import UserDep
from auth.schema import LeaderboardRow
from auth.kpi_service import get_leaderboard_data

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/", response_model=List[LeaderboardRow])
async def get_leaderboard(db: SessionDep, current_user: UserDep):
    """
    Returns the student leaderboard with all KPI metrics and final grant status.
    Sorted by final score in descending order.
    """
    return await get_leaderboard_data(db)
