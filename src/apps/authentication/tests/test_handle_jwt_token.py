import datetime

import settings
from apps.authentication.models import JWTToken
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestHandleJWTToken(AsyncTestCase):
    fixtures = ["users"]

    async def async_set_up(self):
        await super().async_set_up()
        self.user = await User.get(username="test")

    async def test_generate_valid_jwt_token(self):
        token = await JWTToken.get_or_create(self.user)
        assert token.is_valid
        assert "Bearer" == token.token_type

    async def test_refresh_jwt_token(self):
        token = await JWTToken.get_or_create(self.user)
        assert token.can_be_refreshed

        old_token = token.model_dump()

        await token.refresh()
        assert old_token["access_token"] != token.access_token
        assert old_token["id"] == token.id
        assert token.is_valid

    async def test_token_exceeded_refresh_delay(self):
        token = await JWTToken.get_or_create(self.user)
        minutes = (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
            + settings.TOKEN_REFRESH_DELAY_MINUTES
            + 1
        )
        dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            minutes=minutes
        )

        token.created_at = dt.replace(tzinfo=None)
        await token.save()

        assert token.is_valid is False
        assert token.can_be_refreshed is False
