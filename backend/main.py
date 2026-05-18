from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.base import create_db_and_tables
from backend import router


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_db_and_tables()

    yield


app = FastAPI(
    title="Grant LMS Project",
    version="0.1",
    summary="Grant LMS Project API",
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)


app.include_router(router)