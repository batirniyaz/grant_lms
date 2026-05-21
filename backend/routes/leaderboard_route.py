from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect
from typing import List

from db.get_db import SessionDep, async_session_maker
from auth.util import UserDep
from auth.schema import LeaderboardRow
from auth.kpi_service import get_leaderboard_data
from backend.ws_manager import manager

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/", response_model=List[LeaderboardRow])
async def get_leaderboard(db: SessionDep, current_user: UserDep, limit: int = 100, page: int = 1):
    """
    Returns the student leaderboard with all KPI metrics and final grant status.
    Sorted by final score in descending order. Supports pagination.
    """
    return await get_leaderboard_data(db, limit=limit, page=page)


@router.websocket("/ws")
async def leaderboard_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data upon connection
        async with async_session_maker() as db:
            data = await get_leaderboard_data(db)
            # Serialize for JSON transport
            data_json = [row.model_dump(mode='json') for row in data]
            await websocket.send_json({"type": "initial", "data": data_json})

        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

