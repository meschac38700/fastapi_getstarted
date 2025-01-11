from apps.hero.models import Hero
from core.db.fixtures import LoadFixtures
from tests.base import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.loader = LoadFixtures()

    async def test_load_hero_fixtures(self):
        stored_heroes = await Hero.all()
        self.assertEqual(0, len(stored_heroes))

        await self.loader.load_fixtures()

        self.assertEqual(6, self.loader.count_created)

        stored_heroes = await Hero.all()
        self.assertEqual(6, len(stored_heroes))
