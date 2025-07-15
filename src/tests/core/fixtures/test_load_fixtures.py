from pathlib import Path

from apps.user.models import User
from core.services.files.paths import relative_from_src
from core.tasks import load_fixtures_task
from core.unittest.async_case import AsyncTestCase


class TestLoadFixture(AsyncTestCase):
    async def test_load_initial_fixtures(self):
        assert 0 == len(await User.all())

        await self.fixture_loader.load_fixtures()

        assert len(await User.all()) >= 1

    async def test_load_fixtures_filepath(self):
        assert 0 == len(await User.all())

        fixture_path = Path(__file__).parent / "data" / "test_fixtures.yaml"
        await self.fixture_loader.load_fixtures([fixture_path], loader_key="path")

        assert len(await User.all()) == 1

    async def test_load_fixtures_name(self):
        assert 0 == len(await User.all())

        await self.fixture_loader.load_fixtures(["users"])

        assert len(await User.all()) >= 1
        assert self.fixture_loader.count_created >= 1

    async def test_load_fixtures_name_with_extension(self):
        assert 0 == len(await User.all())

        await self.fixture_loader.load_fixtures(["users.yaml"])

        assert len(await User.all()) >= 1
        assert self.fixture_loader.count_created >= 1

    def test_load_initial_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay().get()
        assert count >= 1

    def test_load_app_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay(apps=["user"]).get()
        assert count >= 1

    def test_load_names_fixtures_with_celery_task(self):
        count = load_fixtures_task.delay(
            names=[
                "initial_users",
            ]
        ).get()
        assert count >= 1

    def test_load_paths_fixtures_with_celery_task(self):
        fixture_path = relative_from_src(
            Path(__file__).parent / "data" / "test_fixtures.yaml"
        )
        count = load_fixtures_task.delay(paths=[fixture_path]).get()
        assert count >= 1
