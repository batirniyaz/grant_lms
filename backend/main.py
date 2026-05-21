from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.base import create_db_and_tables
from auth.superuser import create_superuser
from backend import get_main_router


def _rebuild_schema_forward_refs() -> None:
    """Resolve circular Pydantic forward refs (MentorRead <-> GroupRead)."""
    from auth.schema import AdminRead, MentorRead, StudentRead
    from backend.schemas.group_schema import GroupRead

    GroupRead.model_rebuild()
    AdminRead.model_rebuild()
    StudentRead.model_rebuild()
    MentorRead.model_rebuild()


_rebuild_schema_forward_refs()


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_db_and_tables()
    await create_superuser()

    yield


app = FastAPI(
    title="Grant LMS Project",
    version="0.1",
    summary="Grant LMS Project API",
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(get_main_router())
