from unittest.async_case import IsolatedAsyncioTestCase

from core.db import create_db_and_tables, delete_db_and_tables
from services.db import DBService
from settings import settings

BASE_URL = "http://test"
_engine = settings.get_engine()


class AsyncTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await create_db_and_tables(_engine)
        self.db_service = DBService()

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await delete_db_and_tables(_engine)
        await self.db_service.dispose()
