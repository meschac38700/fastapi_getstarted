from unittest.async_case import IsolatedAsyncioTestCase

from httpx import ASGITransport, AsyncClient

from core.db import create_db_and_tables, delete_db_and_tables
from core.db.dependency import DBService
from core.db.fixtures import LoadFixtures
from main import app
from settings import settings

BASE_URL = "http://test"
_engine = settings.get_engine()


class AsyncTestCase(IsolatedAsyncioTestCase):
    fixtures: list[str] | None = None

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await create_db_and_tables(_engine)
        self.db_service = DBService()
        await self._load_fixtures()
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await delete_db_and_tables(_engine)
        await self.db_service.dispose()
        await self.client.aclose()

    async def _load_fixtures(self):
        if not self.fixtures:
            return

        await LoadFixtures().load_fixtures(self.fixtures)
