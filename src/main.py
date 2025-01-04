import secrets
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import select

from configs import db_settings
from core.db import SessionDep, create_heroes
from core.db.handle import create_db_and_tables, delete_db_and_tables
from models import Hero

_engine = db_settings.get_engine()


async def handle_app_start(engine: AsyncEngine):
    """Script to be run after fastapi setup."""
    await create_db_and_tables(engine)
    await create_heroes()


async def handle_app_end(engine: AsyncEngine):
    """Script to be run before fastapi shutdown."""
    await delete_db_and_tables(engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await handle_app_start(_engine)
    yield
    await handle_app_end(_engine)


app = FastAPI(lifespan=lifespan)


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


@app.get("/heroes", name="Get heroes")
async def get_items(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    heroes = await session.exec(select(Hero).offset(offset).limit(limit))
    return heroes.all()
