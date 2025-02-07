import asyncio
from unittest.async_case import IsolatedAsyncioTestCase

from httpx import ASGITransport

from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.user.models import User
from core.db import create_db_and_tables, delete_db_and_tables
from core.db.dependency import DBService
from core.db.fixtures import LoadFixtures
from core.test.client import AsyncClientTest
from main import app
from settings import settings

BASE_URL = "http://test"
_engine = settings.get_engine()


class AsyncTestCase(IsolatedAsyncioTestCase):
    fixtures: list[str] | None = None
    db_service: DBService = None

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.client = AsyncClientTest(
            transport=ASGITransport(app=app), base_url=BASE_URL
        )

    @classmethod
    def setUpClass(cls):
        asyncio.run(create_db_and_tables(_engine))
        asyncio.run(cls._load_fixtures())
        cls.db_service = DBService()

    @classmethod
    def tearDownClass(cls):
        asyncio.run(delete_db_and_tables(_engine))
        asyncio.run(cls.db_service.dispose())

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.client.aclose()

    @classmethod
    async def _load_fixtures(cls):
        if not cls.fixtures:
            return

        await LoadFixtures().load_fixtures(cls.fixtures)

    async def add_permissions(self, item: User | Group, permissions: list[str]):
        _permissions = await Permission.filter(Permission.name.in_(permissions))
        item.permissions.extend(_permissions)
        await item.save()
        self.assertTrue(item.has_permissions(_permissions))
