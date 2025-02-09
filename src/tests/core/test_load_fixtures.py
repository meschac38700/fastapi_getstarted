from apps.hero.models import Hero
from apps.user.models import User
from core.db.fixtures import LoadFixtures
from core.test.async_case import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.delete_all(Hero)
        await self.delete_all(User)
        self.loader = LoadFixtures()

    async def test_load_hero_fixtures_single_file(self):
        self.assertEqual(0, len(await User.all()))

        await self.loader.load_fixtures(["users"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.loader.count_created, 1)

    async def test_load_hero_fixtures_multiple_files(self):
        self.assertEqual(0, len(await Hero.all()))
        self.assertEqual(0, len(await User.all()))

        await self.loader.load_fixtures(["users", "heroes"])

        self.assertGreaterEqual(len(await Hero.all()), 1)
        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.loader.count_created, 1)

    async def test_load_hero_fixtures_with_extension(self):
        self.assertEqual(0, len(await User.all()))

        await self.loader.load_fixtures(["users.yaml"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.loader.count_created, 1)
