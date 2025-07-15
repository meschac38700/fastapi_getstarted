from collections.abc import Callable
from typing import Any

from sqlalchemy import Connection, Table
from sqlmodel import Field

from core.db import SQLTable
from core.db.signals.managers import signal_manager
from core.unittest.async_case import AsyncTestCase

Fn = Callable[..., Any]


class BeforeDropModel(SQLTable, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
    name: str


class AfterDropModel(SQLTable, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
    name: str


class TestSchemaSignals(AsyncTestCase):
    async def _db_exec(self, callback: Fn, **kwargs):
        async with self._engine.connect() as conn:
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

        await self._db_exec(table.drop, checkfirst=True)
        await self._db_exec(table.create)
        assert before_create_table_called

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

        await self._db_exec(table.drop, checkfirst=True)
        await self._db_exec(table.create)
        assert after_create_table_called

    async def test_before_drop_signal(self):
        table = BeforeDropModel.table()
        before_drop_table_called = False

        @signal_manager.before_drop(table)
        def before_drop_table(target: Table, _: Connection, **__):
            nonlocal before_drop_table_called
            before_drop_table_called = target.name == BeforeDropModel.table_name()

        await self._db_exec(table.drop)
        assert before_drop_table_called

    async def test_after_drop_signal(self):
        table = AfterDropModel.table()
        after_drop_table_called = False

        @signal_manager.after_drop(table)
        def after_drop_table(target: Table, _: Connection, **__):
            nonlocal after_drop_table_called
            after_drop_table_called = target.name == AfterDropModel.table_name()

        await self._db_exec(table.drop)
        assert after_drop_table_called
