from sqlmodel.ext.asyncio.session import AsyncSession

from configs import db_settings
from models import Hero


async def create_heroes():
    engine = db_settings.get_engine()
    async with AsyncSession(engine) as session:
        session.add_all(
            [
                Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
                Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
                Hero(name="Iron man", secret_name="Robert Downey Jr", age=59),
                Hero(name="Captain America", secret_name="Chris Evans", age=43),
                Hero(name="Superman", secret_name="Henry Cavill", age=41),
                Hero(name="Deadpond", secret_name="Dive Wilson"),
            ]
        )
        await session.commit()
