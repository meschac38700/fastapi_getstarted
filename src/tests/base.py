from unittest.async_case import IsolatedAsyncioTestCase

from core.db import create_db_and_tables, delete_db_and_tables
from settings import settings

BASE_URL = "http://test"
_engine = settings.get_engine()


class AsyncTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await create_db_and_tables(_engine)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await delete_db_and_tables(_engine)
