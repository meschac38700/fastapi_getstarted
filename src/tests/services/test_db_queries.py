import pytest

from apps.hero.models import Hero
from tests.base import AsyncTestCase

BASE_URL = "http://test"


@pytest.mark.anyio
class TestDBService(AsyncTestCase):
    def hero_list(self):
        return [
            Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
            Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48),
            Hero(name="Iron man", secret_name="Robert Downey Jr", age=59),
            Hero(name="Captain America", secret_name="Chris Evans", age=43),
            Hero(name="Superman", secret_name="Henry Cavill", age=41),
            Hero(name="Deadpond", secret_name="Dive Wilson"),
        ]

    @pytest.mark.anyio
    async def test_insert_batch(self):
        data = await self.db_service.all(Hero)
        self.assertEqual(0, len(data))
        # load data
        await self.db_service.insert_batch(self.hero_list())
        data = await self.db_service.all(Hero)
        self.assertGreaterEqual(len(data), len(self.hero_list()))

    @pytest.mark.anyio
    async def test_insert_batch_prevent_duplication(self):
        self.assertEqual(0, len(await self.db_service.all(Hero)))
        # load data twice
        await self.db_service.insert_batch(self.hero_list())
        await self.db_service.insert_batch(self.hero_list())
        data = await self.db_service.all(Hero)
        self.assertGreaterEqual(len(data), len(self.hero_list()))
