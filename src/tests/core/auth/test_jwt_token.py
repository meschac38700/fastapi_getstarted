import datetime as dt

import jwt
import pytest

from apps.user.models import User
from core.auth import utils as auth_utils
from core.auth.types import JWTPayload


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
    assert auth_utils.decode_jwt_token_from_request(request) == ("", "")

    await client.user_login(user)

    request = client.build_request("POST", "/")
    assert auth_utils.decode_jwt_token_from_request(request) == (
        client.token.token_type,
        client.token.access_token,
    )


@pytest.mark.usefixtures("db")
async def test_decode_jwt_token(client, user, settings):
    await client.user_login(user)

    data = auth_utils.decode_jwt_token(client.token.access_token)
    assert data.sub == user.username
    assert data.iss == settings.server_address

    today = dt.datetime.now(dt.UTC) + dt.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    assert data.exp.date() == today.date()
    assert data.exp.hour == today.hour
    assert data.exp.minute == today.minute


@pytest.mark.usefixtures("db")
async def test_generate_jwt_token(user, settings):
    today = dt.datetime.now(dt.UTC) + dt.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = JWTPayload(sub=user.username, exp=today)
    token = auth_utils.generate_jwt_token(payload)
    assert isinstance(token, str)

    token_info = jwt.get_unverified_header(token)  # NOSONAR
    assert isinstance(token_info, dict)
    assert token_info["alg"] == settings.algorithm
    assert token_info["typ"] == "JWT"
