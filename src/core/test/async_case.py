from unittest.async_case import IsolatedAsyncioTestCase

from httpx import ASGITransport
from sqlmodel import delete

from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.user.models import User
from core.db import SQLTable, create_db_and_tables, delete_db_and_tables
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
    _loaded_once: bool = False

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self._load_once()
        self.client = AsyncClientTest(
            transport=ASGITransport(app=app), base_url=BASE_URL
        )
        self.db_service = DBService()

    async def add_permissions(self, item: User | Group, permissions: list[str]):
        _permissions = await Permission.filter(Permission.name.in_(permissions))
        missing_permissions = [
            perm for perm in _permissions if perm not in item.permissions
        ]
        item.permissions.extend(missing_permissions)
        await item.save()
        self.assertTrue(item.has_permissions(_permissions))

    async def delete_all(self, model: type[SQLTable]):
        # TODO(Eliam): to delete and replace with Database API method truncate table
        _engine = settings.get_engine()
        async with _engine.begin() as session:
            await session.execute(delete(model))
            await session.commit()

    async def _load_fixtures(self):
        if not self.fixtures:
            return

        await LoadFixtures().load_fixtures(self.fixtures)

    async def _load_once(self):
        if self._loaded_once:
            return

        await delete_db_and_tables(_engine)
        await create_db_and_tables(_engine)
        await self._load_fixtures()
        self._loaded_once = True

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.client.aclose()
        await self.db_service.dispose()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._loaded_once = False
