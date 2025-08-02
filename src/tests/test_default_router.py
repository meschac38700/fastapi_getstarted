from http import HTTPStatus
from unittest.mock import patch

from celery import states as celery_states

from core.unittest.async_case import AsyncTestCase


class TestDefaultRouter(AsyncTestCase):
    async def test_load_fixture_endpoint_failed(self, app):
        with patch("core.db.fixtures.loader.settings") as mock_settings:
            mock_settings.INITIAL_FIXTURES = ["user_need_permission"]
            # Should fail because user fixtures require permissions to be loaded first
            response = await self.client.post(app.url_path_for("load-fixtures"))
            assert response.status_code == HTTPStatus.OK

            expected = {
                "status": celery_states.FAILURE,
                "msg": "Loading fixtures process finished.",
                "loaded": 0,
            }
            assert response.json() == expected

    async def test_load_fixture_endpoint(self, app):
        response = await self.client.post(app.url_path_for("load-fixtures"))
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
        response = await self.client.post(app.url_path_for("load-fixtures"))
        assert response.status_code == HTTPStatus.OK
        expected["status"] = celery_states.REJECTED
        expected["msg"] = "Fixtures already loaded."
        expected["loaded"] = 0
        assert response.json() == expected

    async def test_get_secret(self, app):
        response = await self.client.get(app.url_path_for("secret-key"))
        assert HTTPStatus.OK == response.status_code
        data = response.json()
        assert "secret" in data
        assert len(data["secret"]) > 65

    async def test_get_secret_with_length(self, app):
        length = 55
        response = await self.client.get(
            app.url_path_for("secret-key"), params={"length": length}
        )
        assert len(response.json()["secret"]) > length

    async def test_heath_check(self, app):
        response = await self.client.get(app.url_path_for("health-check"))
        expected_response = {"status": "ok"}

        assert response.status_code == HTTPStatus.OK
        assert expected_response == response.json()
