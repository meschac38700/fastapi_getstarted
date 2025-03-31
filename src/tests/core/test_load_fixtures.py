from apps.authorization.models import Permission
from apps.user.models import User
from core.testing.async_case import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await User.truncate()

    async def test_load_hero_fixtures_single_file(self):
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures(["users"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.fixture_loader.count_created, 1)

    async def test_load_hero_fixtures_multiple_files(self):
        self.assertEqual(0, len(await Permission.all()))
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures(["users", "permissions"])

        self.assertGreaterEqual(len(await Permission.all()), 1)
        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.fixture_loader.count_created, 1)

    async def test_load_hero_fixtures_with_extension(self):
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures(["users.yaml"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.fixture_loader.count_created, 1)
