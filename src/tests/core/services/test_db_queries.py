import pytest
from sqlalchemy.exc import IntegrityError

from apps.user.models import User
from core.unittest.async_case import AsyncTestCase

BASE_URL = "https://test"


def user_list():
    return [
        User(
            password=(lambda: "test1")(),
            username="u_spider",
            first_name="Spider-Boy",
            last_name="Pedro Parqueador",
        ),
        User(
            password=(lambda: "test1")(),
            username="u_rusty",
            first_name="Rusty-Man",
            last_name="Tommy Sharp",
            age=48,
        ),
        User(
            password=(lambda: "test1")(),
            username="u_iron",
            first_name="Iron man",
            last_name="Robert Downey Jr",
            age=59,
        ),
        User(
            password=(lambda: "test1")(),
            username="u_captain",
            first_name="Captain America",
            last_name="Chris Evans",
            age=43,
        ),
        User(
            password=(lambda: "test1")(),
            username="u_superman",
            first_name="Superman",
            last_name="Henry Cavill",
            age=41,
        ),
        User(
            password=(lambda: "test1")(),
            username="u_deadpond",
            first_name="Deadpond",
            last_name="Dive Wilson",
        ),
    ]


class TestDBService(AsyncTestCase):
    async def test_bulk_create_or_update(self):
        await User.truncate()
        data = await self.db_service.all(User)
        assert 0 == len(data)
        # load data
        await self.db_service.bulk_create_or_update(user_list())
        data = await self.db_service.all(User)
        assert len(data) >= len(user_list())

    async def test_bulk_create_or_update_prevent_duplication(self):
        # load data twice
        await self.db_service.truncate(User)
        assert 0 == await self.db_service.count(User)

        await self.db_service.bulk_create_or_update(user_list())
        assert await self.db_service.count(User) > 0

        with pytest.raises(IntegrityError) as e:
            await self.db_service.bulk_create_or_update(user_list())

        assert (
            'duplicate key value violates unique constraint "ix_users_username"'
            in str(e.value)
        )
        assert len(user_list()) == await self.db_service.count(User)

    async def test_bulk_delete(self):
        await self.db_service.truncate(User)
        assert await self.db_service.count(User) == 0

        await self.db_service.bulk_create_or_update(user_list())
        assert await User.count() > 0

        await self.db_service.bulk_delete(await User.all())

        items = await self.db_service.all(User)
        assert [] == items

    async def test_count(self):
        await self.db_service.truncate(User)
        assert await self.db_service.count(User) == 0

        await self.db_service.bulk_create_or_update(user_list())
        assert await User.count() > 0

        assert 1 == await User.count(username="u_deadpond")
        assert await User.count(username__istartswith="u_") >= 1

        await self.db_service.bulk_delete(await User.all())
        assert 0 == await User.count()

    async def test_first(self):
        await self.db_service.truncate(User)
        assert await self.db_service.count(User) == 0

        await self.db_service.bulk_create_or_update(user_list())
        assert await User.count() > 0

        assert await self.db_service.count(User) > 0
        user = await self.db_service.first(User)
        assert isinstance(user, User)
        assert user.username == "u_spider"
        assert user.first_name == "Spider-Boy"
        assert user.last_name == "Pedro Parqueador"
