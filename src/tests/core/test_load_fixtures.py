from apps.hero.models import Hero
from core.db.fixtures import LoadFixtures
from core.test.async_case import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.loader = LoadFixtures()

    async def test_load_hero_fixtures(self):
        stored_heroes = await Hero.all()
        self.assertEqual(0, len(stored_heroes))

        await self.loader.load_fixtures(["users", "heroes"])

        self.assertGreaterEqual(self.loader.count_created, 1)
