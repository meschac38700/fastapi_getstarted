import pytest

from apps.hero import Hero
from apps.hero.faker import fake_heroes, hero_list
from services.db import DBService
from tests.base import AsyncTestCase

BASE_URL = "http://test"


@pytest.mark.anyio
class TestDBService(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.db_service = DBService()

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.db_service.dispose()

    @pytest.mark.anyio
    async def test_insert_batch(self):
        data = await self.db_service.all(Hero)
        self.assertEqual(0, len(data))
        # load data
        await fake_heroes(self.db_service)
        data = await self.db_service.all(Hero)
        self.assertGreaterEqual(len(data), len(hero_list()))

    @pytest.mark.anyio
    async def test_insert_batch_prevent_duplication(self):
        await self.db_service.all(Hero)
        # load data twice
        await fake_heroes(self.db_service)
        data = await self.db_service.all(Hero)
        self.assertGreaterEqual(len(data), len(hero_list()))
