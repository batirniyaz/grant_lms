
import os
import sys


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter
from sqlalchemy import text
from db.get_db import SessionCtx, SessionDep
import asyncio



router = APIRouter()



@router.get("/test_conn")
async def test_connection(session: SessionDep):
    print(f"using session: {session}")
    # execute a simple query to validate the connection
    result = await session.execute(text("SELECT 1"))
    print(result)
    return {"status": "ok"}


async def _main():
    async with SessionCtx() as session:
        resp = await test_connection(session)
        print("endpoint response:", resp)


if __name__ == "__main__":

    asyncio.run(_main())
