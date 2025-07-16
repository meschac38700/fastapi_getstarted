from datetime import datetime, timedelta

import pytest

import settings
from apps.user.models import User
from core.auth import utils as auth_utils


@pytest.fixture
async def user(db):  # pylint: disable=unused-argument
    return await User(
        username="user",
        first_name="first",
        last_name="last",
        password=(lambda: "password")(),
    ).save()


@pytest.mark.usefixtures("db")
async def test_token_from_request(client, user):
    request = client.build_request("POST", "/")
    assert auth_utils.jwt_token_from_request(request) == ("", "")

    await client.user_login(user)

    request = client.build_request("POST", "/")
    assert auth_utils.jwt_token_from_request(request) == (
        client.token.token_type,
        client.token.access_token,
    )


@pytest.mark.usefixtures("db")
async def test_decode_jwt_token(client, user):
    await client.user_login(user)

    data = auth_utils.decode_jwt_token(client.token.access_token)
    assert data["sub"] == user.username
    assert isinstance(data["exp"], int)

    today = datetime.today() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    exp = datetime.fromtimestamp(data["exp"])
    assert exp.date() == today.date()
    assert exp.hour == today.hour
    assert exp.minute == today.minute
