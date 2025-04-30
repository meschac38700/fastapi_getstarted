from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Mapper

from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.testing.async_case import AsyncTestCase


class TestMapperSignal(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.user = await User.get(id=1)

    async def test_before_update_signal(self):
        def double_user_age(_: Mapper[User], __: Connection, user: User):
            user.age *= 2

        new_age = 10
        signal_manager.before_update(User)(double_user_age)
        self.user.age = new_age
        await self.user.save()

        self.assertEqual(new_age * 2, self.user.age)

    async def test_after_update_signal(self):
        def double_user_age(_: Mapper[User], __: Connection, user: User):
            user.age *= 2

        new_age = 10
        signal_manager.after_update(User)(double_user_age)
        self.user.age = new_age
        await self.user.save()

        self.assertEqual(new_age, self.user.age)
        self.assertNotEqual(new_age * 2, self.user.age)
