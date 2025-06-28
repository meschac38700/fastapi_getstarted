import asyncio
from http import HTTPStatus

from celery import states as celery_states

from apps.authorization.models import Permission
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase
from settings import settings


class TestDefaultRouter(AsyncTestCase):
    async def test_load_fixture_endpoint_failed(self):
        # Should fail because user fixtures require permissions to be loaded first
        response = await self.client.post("/fixtures")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected = {
            "status": celery_states.FAILURE,
            "msg": "Loading fixtures process finished.",
            "loaded": 0,
        }
        self.assertEqual(response.json(), expected)

    async def test_load_fixture_endpoint(self):
        await asyncio.gather(
            Permission.generate_crud_objects(Permission.table_name()),
            Permission.generate_crud_objects(User.table_name()),
        )

        response = await self.client.post("/fixtures")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        expected = {
            "status": celery_states.SUCCESS,
            "msg": "Loading fixtures process finished.",
            "loaded": 7,
        }

        self.assertEqual(response.json(), expected)

        # Failed: Integrity error.
        response = await self.client.post("/fixtures")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        expected["status"] = celery_states.REJECTED
        expected["loaded"] = 0
        self.assertEqual(response.json(), expected)

    async def test_get_secret(self):
        response = await self.client.get("/")
        assert HTTPStatus.OK == response.status_code
        data = response.json()
        assert "secret" in data
        assert len(data["secret"]) > 65

    async def test_get_secret_with_length(self):
        length = 55
        response = await self.client.get("/", params={"length": length})
        assert len(response.json()["secret"]) > length

    async def test_heath_check(self):
        response = await self.client.get(settings.health_check_endpoint)
        expected_response = {"status": "ok"}

        assert response.status_code == HTTPStatus.OK
        assert expected_response == response.json()
