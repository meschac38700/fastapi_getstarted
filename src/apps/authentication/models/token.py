import datetime
from typing import Self

import jwt
from sqlmodel import Field, Relationship

import settings
from apps.authentication import utils
from apps.user.models import User

from ._base import JWTTokenSQLBaseModel


class JWTToken(JWTTokenSQLBaseModel, table=True):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    user: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})

    @property
    def is_expired(self) -> bool:
        token_refresh_safety_minutes = 5
        expiration_time = utils.token_expire_datetime(self.created_at)
        # we refresh token 5minutes before the real expiration time.
        safety_now_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=token_refresh_safety_minutes)
        return expiration_time < safety_now_time

    @property
    def is_valid(self):
        return not self.is_expired

    @property
    def can_be_refreshed(self):
        if self.is_valid:
            return True

        expired_dt = utils.token_expire_datetime(self.created_at)
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - expired_dt
        return (delta.seconds / 60) <= settings.TOKEN_REFRESH_DELAY_MINUTES

    @classmethod
    async def _create(cls, user: User):
        return await cls(access_token=cls._generate_jwt_token(user), user=user).save()

    @classmethod
    async def get_or_create(cls, user: User) -> Self:
        token = await cls.get(cls.user_id == user.id)
        if token is not None and not token.is_expired:
            return token

        return await cls._create(user)

    async def refresh(self):
        dt = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        data = {
            "access_token": JWTToken._generate_jwt_token(self.user),
            "created_at": dt,
        }
        self.update_from_dict(data)
        await self.save()

    @classmethod
    def _generate_jwt_token(cls, user: User, exp: datetime.datetime | None = None):
        exp = exp or utils.token_expire_datetime()
        to_encode = {
            "sub": user.username,
            "exp": exp.isoformat(),
        }
        _settings = settings.get_settings()
        return jwt.encode(
            to_encode, _settings.secret_key, algorithm=_settings.algorithm
        )
