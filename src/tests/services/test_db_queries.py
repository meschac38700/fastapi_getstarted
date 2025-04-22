import pytest
from sqlalchemy.exc import IntegrityError

from apps.user.models import User
from core.testing.async_case import AsyncTestCase

BASE_URL = "http://test"


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

    async def test_insert_batch(self):
        await User.truncate()
        data = await self.db_service.all(User)
        self.assertEqual(0, len(data))
        # load data
        await self.db_service.insert_batch(self.user_list())
        data = await self.db_service.all(User)
        self.assertGreaterEqual(len(data), len(self.user_list()))

    async def test_insert_batch_prevent_duplication(self):
        # load data twice
        await self.db_service.insert_batch(self.user_list())
        with pytest.raises(IntegrityError) as e:
            await self.db_service.insert_batch(self.user_list())
        self.assertIn(
            'duplicate key value violates unique constraint "ix_users_username"',
            str(e.value),
        )
        data = await self.db_service.all(User)
        self.assertGreaterEqual(len(data), len(self.user_list()))
