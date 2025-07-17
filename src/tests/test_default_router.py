from http import HTTPStatus
from unittest.mock import patch

from celery import states as celery_states

from core.unittest.async_case import AsyncTestCase
from settings import settings


class TestDefaultRouter(AsyncTestCase):
    async def test_load_fixture_endpoint_failed(self):
        with patch("core.db.fixtures.loader.settings") as mock_settings:
            mock_settings.INITIAL_FIXTURES = ["user_need_permission"]
            # Should fail because user fixtures require permissions to be loaded first
            response = await self.client.post("/fixtures")
            assert response.status_code == HTTPStatus.OK

            expected = {
                "status": celery_states.FAILURE,
                "msg": "Loading fixtures process finished.",
                "loaded": 0,
            }
            assert response.json() == expected

    async def test_load_fixture_endpoint(self):
        response = await self.client.post("/fixtures")
        assert response.status_code == HTTPStatus.OK
        expected = {
            "status": celery_states.SUCCESS,
            "msg": "Loading fixtures process finished.",
            "loaded": 1,
        }
        assert response.json()["status"] == expected["status"]
        assert response.json()["msg"] == expected["msg"]
        assert response.json()["loaded"] >= expected["loaded"]

        # Failed: Integrity error.
        response = await self.client.post("/fixtures")
        assert response.status_code == HTTPStatus.OK
        expected["status"] = celery_states.REJECTED
        expected["loaded"] = 0
        assert response.json() == expected

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
