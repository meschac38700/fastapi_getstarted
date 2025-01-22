from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from core.lifespan import setup, teardown
from core.routers import register_default_endpoints
from core.routers.register import AppRouter
from settings import settings

_engine = settings.get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await setup(_engine)
    yield
    await teardown(_engine)


app = FastAPI(lifespan=lifespan)
register_default_endpoints(app)
# register routers from apps directory
AppRouter().register_all(app)


def main():
    from apps.hero.models import Hero

    hero_1 = Hero(id=1, name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(id=2, name="Deadpond1", secret_name="Dive Wilson1")
    hero_3 = Hero(name="Deadpond3", secret_name="Dive Wilson2")
    with Session(_engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.commit()
        session.refresh(hero_1)
        session.refresh(hero_2)
        session.refresh(hero_3)


if __name__ == "__main__":
    main()
