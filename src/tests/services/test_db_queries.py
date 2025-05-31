import pytest
from sqlalchemy.exc import IntegrityError

from apps.user.models import User
from core.unittest.async_case import AsyncTestCase

BASE_URL = "https://test"


class TestDBService(AsyncTestCase):
    def user_list(self):
        return [
            User(
                password="test1",
                username="u_spider",
                first_name="Spider-Boy",
                last_name="Pedro Parqueador",
            ),
            User(
                password="test1",
                username="u_rusty",
                first_name="Rusty-Man",
                last_name="Tommy Sharp",
                age=48,
            ),
            User(
                password="test1",
                username="u_iron",
                first_name="Iron man",
                last_name="Robert Downey Jr",
                age=59,
            ),
            User(
                password="test1",
                username="u_captain",
                first_name="Captain America",
                last_name="Chris Evans",
                age=43,
            ),
            User(
                password="test1",
                username="u_superman",
                first_name="Superman",
                last_name="Henry Cavill",
                age=41,
            ),
            User(
                password="test1",
                username="u_deadpond",
                first_name="Deadpond",
                last_name="Dive Wilson",
            ),
        ]

    async def test_bulk_create_or_update(self):
        await User.truncate()
        data = await self.db_service.all(User)
        self.assertEqual(0, len(data))
        # load data
        await self.db_service.bulk_create_or_update(self.user_list())
        data = await self.db_service.all(User)
        self.assertGreaterEqual(len(data), len(self.user_list()))

    async def test_bulk_create_or_update_prevent_duplication(self):
        # load data twice
        await self.db_service.bulk_create_or_update(self.user_list())
        with pytest.raises(IntegrityError) as e:
            await self.db_service.bulk_create_or_update(self.user_list())
        self.assertIn(
            'duplicate key value violates unique constraint "ix_users_username"',
            str(e.value),
        )
        data = await self.db_service.all(User)
        self.assertGreaterEqual(len(data), len(self.user_list()))

    async def test_bulk_delete(self):
        list_item = self.user_list()
        await self.db_service.bulk_create_or_update(list_item)

        await self.db_service.bulk_delete(list_item)

        items = await self.db_service.all(User)
        self.assertEqual([], items)

    async def test_count(self):
        list_item = self.user_list()
        await self.db_service.bulk_create_or_update(list_item)
        expected_count = len(list_item)
        actual_count = await User.count()

        self.assertEqual(actual_count, expected_count)

        self.assertEqual(1, await User.count(username="u_deadpond"))

        self.assertGreaterEqual(await User.count(username__istartswith="u_"), 1)

        await self.db_service.bulk_delete(list_item)
        self.assertEqual(0, await User.count())
