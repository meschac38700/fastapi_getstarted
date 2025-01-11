from core.db.dependency import DBService

from .models import Hero


def hero_list():
    return [
        Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
        Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
        Hero(name="Iron man", secret_name="Robert Downey Jr", age=59),
        Hero(name="Captain America", secret_name="Chris Evans", age=43),
        Hero(name="Superman", secret_name="Henry Cavill", age=41),
        Hero(name="Deadpond", secret_name="Dive Wilson"),
    ]


async def fake_heroes(db_service: DBService):
    """Initialize fake hero data if not already exist.

    Called by: core.lifespan.py
    """

    filters = Hero.name in [hero.name for hero in hero_list()]
    already_exists = await Hero.get(filters)
    if already_exists is not None:
        return

    await Hero.batch_create(hero_list())
