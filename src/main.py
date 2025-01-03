import secrets
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.params import Query
from sqlmodel import Session, select

from configs import db_settings
from models import Hero


def create_db_and_tables():
    """Script to be run after fastapi setup."""


def delete_db_and_tables():
    """Script to be run before fastapi shutdown."""


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield
    delete_db_and_tables()


app = FastAPI(lifespan=lifespan)
engine = db_settings.get_engine()


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/heroes", name="Init items")
async def create_heros(session: SessionDep):
    async with session.begin():
        session.add_all(
            [
                Hero(name="Deadpond", secret_name="Dive Wilson"),
                Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
                Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
            ]
        )


@app.get("/heroes", name="Get heroes")
async def get_items(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
