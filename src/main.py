import secrets
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.params import Query
from sqlmodel import Session, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from configs import db_settings
from models import Hero

engine = db_settings.get_engine()


async def create_db_and_tables():
    """Script to be run after fastapi setup."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def delete_db_and_tables():
    """Script to be run before fastapi shutdown."""


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield
    delete_db_and_tables()


app = FastAPI(lifespan=lifespan)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/heroes", name="Init items")
async def create_heroes(session: SessionDep):
    session.add_all(
        [
            Hero(name="Deadpond", secret_name="Dive Wilson"),
            Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
            Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
            Hero(name="Iron man", secret_name="Robert Downey Jr", age=59),
            Hero(name="Captain America", secret_name="Chris Evans", age=43),
            Hero(name="Superman", secret_name="Henry Cavill", age=41),
        ]
    )
    await session.commit()


@app.get("/heroes", name="Get heroes")
async def get_items(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    heroes = await session.exec(select(Hero).offset(offset).limit(limit))
    return heroes.all()
