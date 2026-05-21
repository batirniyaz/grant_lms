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


@router.get("/pdp-market")
async def get_pdp_market(current_user: UserDep, db: SessionDep):
    # Hardcoded product catalog
    products = [
        {"id": 1, "name": "PDP Portfolio", "price": 150, "image": "portfolio.png"},
        {"id": 2, "name": "Mechanical Keyboard", "price": 300, "image": "keyboard.png"},
        {"id": 3, "name": "PDP Online Course", "price": 750, "image": "course.png"},
        {"id": 4, "name": "High-end Mouse", "price": 200, "image": "mouse.png"},
    ]
    
    # Calculate potential points for the current student
    leaderboard = await get_leaderboard_data(db)
    student_data = next((s for s in leaderboard if s.student_id == current_user['id']), None)
    
    potential_points = int(student_data.final_score * 10) if student_data else 0
    
    return {
        "products": products,
        "student_balance": 0, # Placeholder for actual stored balance
        "potential_points": potential_points
    }

