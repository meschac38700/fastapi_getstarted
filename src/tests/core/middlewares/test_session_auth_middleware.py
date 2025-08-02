from fastapi import status


async def test_skip_session_auth_middleware_test_environment(client, settings, app):
    settings.TEST_BASE_URL = "https://example.dev"
    response = await client.get(app.url_path_for("session-login"))
    assert response.status_code == status.HTTP_200_OK


async def test_skip_session_auth_middleware_if_xhr(client, settings, app):
    settings.TEST_BASE_URL = "https://example.dev"
    response = await client.get(app.url_path_for("session-login"))
    assert response.status_code == status.HTTP_200_OK
