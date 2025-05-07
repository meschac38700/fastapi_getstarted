from collections.abc import Callable
from typing import Any

from sqlalchemy import Connection, Table
from sqlmodel import Field

from core.db import SQLTable
from core.db.signals.managers import signal_manager
from core.testing.async_case import AsyncTestCase
from settings import settings

Fn = Callable[..., Any]


class TestSchemaSignals(AsyncTestCase):
    async def _db_exec(self, callback: Fn, **kwargs):
        engine = settings.get_engine()
        async with engine.connect() as conn:
            await conn.run_sync(lambda sync_conn: callback(sync_conn, **kwargs))

    async def test_before_create_signal(self):
        class BeforeCreateModel(SQLTable, table=True):
            id: int = Field(primary_key=True, allow_mutation=False)
            name: str

        table = BeforeCreateModel.table()
        before_create_table_called = False

        @signal_manager.before_create(table)
        def before_create_table(target: Table, _: Connection, **__):
            """Listener for before create model table."""
            nonlocal before_create_table_called
            before_create_table_called = target.name == BeforeCreateModel.table_name()

        await self._db_exec(table.create)
        self.assertTrue(before_create_table_called)

    async def test_after_create_signal(self):
        class AfterCreateModel(SQLTable, table=True):
            id: int = Field(primary_key=True, allow_mutation=False)
            name: str

        table = AfterCreateModel.table()

        after_create_table_called = False

        @signal_manager.after_create(table)
        def after_create_table(target: Table, _: Connection, **__):
            nonlocal after_create_table_called
            after_create_table_called = target.name == AfterCreateModel.table_name()

        await self._db_exec(table.create)
        self.assertTrue(after_create_table_called)
