from typing import Optional

import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine

from apps.authorization.models import Group, Permission
from apps.user.models import User
from core.db import create_all_tables, delete_all_tables
from core.db.dependencies import DBService
from core.db.fixtures import LoadFixtures
from core.unittest.client import AsyncClientTest
from main import app

BASE_URL = "https://test"


@pytest.mark.usefixtures("create_db")
class AsyncTestCase:
    fixtures: Optional[list[str]] = None
    db_service: DBService = None
    fixture_loader = LoadFixtures()
    _engine: Optional[AsyncEngine] = None
    client = None

    @pytest.fixture(scope="function", autouse=True)
    async def create_db(self, db: AsyncEngine, settings):
        self._engine = db
        self.db_service = DBService()
        await self._load_fixtures()
        await self.asyncSetUp()
        yield
        await self.asyncTearDown()

    async def asyncSetUp(self):
        """Setup before each test"""
        self.client = AsyncClientTest(
            transport=ASGITransport(app=app), base_url=BASE_URL
        )

    async def add_permissions(self, item: User | Group, permission_names: list[str]):
        _permissions = await Permission.filter(name__in=permission_names)
        missing_permissions = [
            perm for perm in _permissions if perm not in item.permissions
        ]
        item.permissions.extend(missing_permissions)
        await item.save()
        assert item.has_permissions(_permissions)

    async def _load_fixtures(self):
        if not self.fixtures:
            return

        await delete_all_tables(self._engine)
        await create_all_tables(self._engine)
        await self.fixture_loader.load_fixtures(self.fixtures)

    async def asyncTearDown(self):
        await self.client.aclose()
