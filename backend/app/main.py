from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (ลงทะเบียน Model ก่อน create_all)
from app.core.database import Base, engine
from app.routes.api import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Mini Project: ใช้ create_all; งานจริงควรใช้ Alembic migration
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PetTech API", lifespan=lifespan)
app.include_router(router)
