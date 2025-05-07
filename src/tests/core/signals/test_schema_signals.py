from sqlalchemy import Connection, Table

from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.testing.async_case import AsyncTestCase


class TestSchemaSignals(AsyncTestCase):
    def register_listeners(self):
        @signal_manager.before_create(User.table())
        def before_create_user_table(target: Table, _: Connection, **__):
            self.before_create_user_table_called = target.name == User.table_name()

        @signal_manager.after_create(User.table())
        def after_create_user_table(target: Table, _: Connection, **__):
            self.after_create_user_table_called = target.name == User.table_name()

    async def asyncSetUp(self):
        self.before_create_user_table_called = False
        self.after_create_user_table_called = False
        self.register_listeners()
        await super().asyncSetUp()

    def test_before_create_signal(self):
        self.assertTrue(self.before_create_user_table_called)

    def test_after_create_signal(self):
        self.assertTrue(self.after_create_user_table_called)
