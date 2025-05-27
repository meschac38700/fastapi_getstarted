import asyncio
from pathlib import Path

from typer.testing import CliRunner

from apps.authorization.models import Permission
from apps.user.models import User
from core.tasks import load_fixtures_task
from core.testing.async_case import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await asyncio.gather(
            Permission.generate_crud_objects(Permission.table_name()),
            Permission.generate_crud_objects(User.table_name()),
        )
        await User.truncate()
        self.cli_runner = CliRunner()

    async def test_load_initial_fixtures(self):
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures()

        self.assertGreaterEqual(len(await User.all()), 1)

    async def test_load_fixtures_filepath(self):
        self.assertEqual(0, len(await User.all()))

        fixture_path = Path(__file__).parent / "data" / "test_fixtures.yaml"
        await self.fixture_loader.load_fixtures([fixture_path], loader_key="path")

        self.assertGreaterEqual(len(await User.all()), 1)

    async def test_load_fixtures_name(self):
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures(["users"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.fixture_loader.count_created, 1)

    async def test_load_fixtures_name_with_extension(self):
        self.assertEqual(0, len(await User.all()))

        await self.fixture_loader.load_fixtures(["users.yaml"])

        self.assertGreaterEqual(len(await User.all()), 1)
        self.assertGreaterEqual(self.fixture_loader.count_created, 1)

    async def test_load_initial_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay().get()
        self.assertGreaterEqual(count, 1)

    async def test_load_app_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay(apps=["user"]).get()
        self.assertGreaterEqual(count, 1)

    async def test_load_names_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay(
            names=[
                "initial_users",
            ]
        ).get()
        self.assertGreaterEqual(count, 1)
