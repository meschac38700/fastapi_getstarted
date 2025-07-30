import re

import pytest
from fastapi import FastAPI, status

from apps.user.models import User
from core.templating.utils import render_string
from core.unittest.client import AsyncClientTest


async def test_get_session_login_form(
    client: AsyncClientTest, app: FastAPI, http_request
):
    response = await client.get(app.url_path_for("session-login"))
    assert response.status_code == status.HTTP_200_OK
    html_response = response.content.decode()
    expected_html = render_string(http_request, "authentication/login.html")

    # bypass csrf_token
    html_response = re.sub(
        re.compile(r'name="csrf_token" value="\w+"'),
        'name="csrf_token" value="None"',
        html_response,
    )

    assert expected_html == html_response


async def test_session_login(
    client: AsyncClientTest,
    app: FastAPI,
    user,
    csrf_token,
    settings,
):
    # pre check
    response = await client.get(app.url_path_for("chat-template"))
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    login_data = {
        settings.token_key: csrf_token,
        "username": user.username,
        "password": (lambda: "password")(),
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND  # redirection after connexion
    assert response.next_request.url.path == settings.session_auth_redirect_success
    session = response.cookies.get(settings.session_cookie)
    assert isinstance(session, str)

    # post check
    response = await client.get(app.url_path_for("chat-template"))
    assert response.status_code == status.HTTP_200_OK


async def test_session_logout(client, app, user, csrf_token, settings):
    # ensure that user is not logged
    assert client.cookies.get(settings.session_cookie) is None

    # login the user
    login_data = {
        settings.token_key: csrf_token,
        "username": user.username,
        "password": (lambda: "password")(),
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND  # redirection after connexion

    # check user is logged
    assert client.cookies.get(settings.session_cookie) is not None

    response = await client.post(app.url_path_for("session-logout"))
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.SESSION_AUTH_URL
    assert client.cookies.get(settings.session_cookie) is None


@pytest.mark.usefixtures("db")
async def test_register_new_user_with_session_auth(client, app, csrf_token, settings):
    user_data = {
        settings.token_key: csrf_token,
        "username": "session",
        "password": (lambda: "password")(),
        "first_name": "Session",
        "last_name": "Pytest",
    }
    assert client.cookies.get(settings.session_cookie) is None

    response = await client.post(app.url_path_for("session-register"), data=user_data)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.cookies.get(settings.session_cookie) is not None
    assert client.cookies.get(settings.session_cookie) is not None
    assert response.next_request.url.path == settings.session_auth_redirect_success

    created_user = await User.get(username=user_data["username"])
    assert created_user is not None
    assert created_user.check_password(user_data["password"])

    # try to access to register view while authenticated -> redirect
    response = await client.get(app.url_path_for("session-register"))
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.session_auth_redirect_success
