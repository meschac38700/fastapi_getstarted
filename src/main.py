import secrets

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from configs import engine
from models.base import BaseAsyncModel
from models.items import Item

app = FastAPI()


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


async def get_items():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session.begin() as conn:
        await conn.run_sync(BaseAsyncModel.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    Item(name="Item 1"),
                    Item(name="Item 2"),
                    Item(name="Item 3"),
                ]
            )

    await engine.dispose()
