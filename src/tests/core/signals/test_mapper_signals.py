import asyncio

from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Mapper

from apps.authorization.models import Permission
from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.testing.async_case import AsyncTestCase


class TestMapperSignal(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self, *args, **kwargs):
        await super().asyncSetUp()
        self.user, self.second_user = await asyncio.gather(
            User.get(id=1), User.get(id=2)
        )

    async def test_before_update_signal(self):
        def double_user_age(_: Mapper[User], __: Connection, user: User):
            user.age *= 2

        new_age = 10
        signal_manager.before_update(User)(double_user_age)
        self.user.age = new_age
        await self.user.save()

        self.assertEqual(new_age * 2, self.user.age)

        # Unregister to avoid distorting next tests
        signal_manager.unregister("before_update", double_user_age, target=User)

    async def test_after_update_signal(self):
        def set_second_user_age(_: Mapper[User], __: Connection, user: User):
            self.second_user.age = user.age * -1

        new_age = 10
        signal_manager.after_update(User)(set_second_user_age)
        self.user.age = new_age
        await self.user.save()

        self.assertEqual(new_age, self.user.age)
        self.assertEqual(self.second_user.age, new_age * -1)

        # Unregister to avoid distorting next tests
        signal_manager.unregister("after_update", set_second_user_age, target=User)

    async def test_before_insert_signal(self):
        permissions = await Permission.filter(target_table=User.table_name())

        def set_permissions(_: Mapper[User], __: Connection, user: User):
            user.permissions = permissions

        signal_manager.before_insert(User)(set_permissions)
        new_user = await User(
            username="foo", first_name="bar", last_name="DOE", password="pytest"
        ).save()

        self.assertEqual(new_user.permissions, permissions)

        # Unregister to avoid distorting next tests
        signal_manager.unregister("before_insert", set_permissions, target=User)
