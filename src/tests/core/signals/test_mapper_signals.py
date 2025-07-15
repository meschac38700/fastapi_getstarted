import pytest
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Mapper

from apps.authorization.models import Permission
from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.db.signals.utils.types import EventCategory
from core.unittest.async_case import AsyncTestCase


class DeletionProhibitedError(Exception):
    pass


class TestMapperSignal(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self, *_, **__):
        await super().asyncSetUp()
        self.user = await User.first()
        self.second_user = (await User.filter(username__not_equals=self.user.username))[
            0
        ]

    async def test_before_update_signal(self):
        def double_user_age(_: Mapper[User], __: Connection, user: User):
            user.age *= 2

        new_age = 10
        signal_manager.before_update(User)(double_user_age)
        self.user.age = new_age
        await self.user.save()

        assert new_age * 2 == self.user.age

        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "before_update", double_user_age, target=User, category=EventCategory.MAPPER
        )

    async def test_after_update_signal(self):
        def set_second_user_age(_: Mapper[User], __: Connection, user: User):
            self.second_user.age = user.age * -1

        new_age = 10
        signal_manager.after_update(User)(set_second_user_age)
        self.user.age = new_age
        await self.user.save()

        assert new_age == self.user.age
        assert self.second_user.age == new_age * -1

        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "after_update",
            set_second_user_age,
            target=User,
            category=EventCategory.MAPPER,
        )

    async def test_before_insert_signal(self):
        permissions = await Permission.filter(target_table=User.table_name())

        def set_permissions(_: Mapper[User], __: Connection, user: User):
            user.permissions = permissions

        signal_manager.before_insert(User)(set_permissions)
        new_user = await User(
            username="before_insert_user",
            first_name="bar",
            last_name="DOE",
            password=(lambda: "pytest")(),
        ).save()

        assert new_user.permissions == permissions

        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "before_insert", set_permissions, target=User, category=EventCategory.MAPPER
        )

    async def test_after_insert_signal(self):
        permissions = list(await Permission.filter(target_table=User.table_name()))

        def copy_permissions(_: Mapper[User], __: Connection, user: User):
            self.user.permissions = user.permissions

        signal_manager.after_insert(User)(copy_permissions)
        new_user = await User(
            username="after_insert_user",
            first_name="bar",
            last_name="DOE",
            password=(lambda: "pytest")(),
            permissions=permissions,
        ).save()

        assert self.user.permissions == new_user.permissions

        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "after_insert", copy_permissions, target=User, category=EventCategory.MAPPER
        )

    async def test_before_delete_signal(self):
        def deny_deletion(_: Mapper[User], __: Connection, user: User):
            raise DeletionProhibitedError(f"Cannot delete user {user.id}.")

        signal_manager.before_delete(User)(deny_deletion)
        with pytest.raises(DeletionProhibitedError) as e:
            await self.second_user.delete()

        await self.second_user.refresh()
        assert self.second_user is not None
        assert f"Cannot delete user {self.second_user.id}." == str(e.value)

        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "before_delete", deny_deletion, target=User, category=EventCategory.MAPPER
        )

    async def test_after_delete_signal(self):
        called = False

        def check_called(_: Mapper[User], __: Connection, ___: User):
            nonlocal called
            called = True

        pk = self.second_user.id
        signal_manager.after_delete(User)(check_called)
        await self.second_user.delete()
        assert called
        assert await User.get(id=pk) is None
        # Unregister to avoid distorting next tests
        signal_manager.unregister(
            "after_delete", check_called, target=User, category=EventCategory.MAPPER
        )

    async def test_signal_after_bulk_delete(self):
        called_count = 0

        @signal_manager.after_delete(User)
        def count_called(_: Mapper[User], __: Connection, ___: User):
            nonlocal called_count
            called_count += 1

        users = await User.all()
        expected_called_count = len(users)
        await User.bulk_delete(users)
        assert expected_called_count == called_count
