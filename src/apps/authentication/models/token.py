import datetime
from typing import Self

from sqlmodel import Field, Relationship

from apps.user.models import User
from core.auth import utils as auth_utils
from core.auth.types import JWTPayload
from settings import settings

from ._base import JWTTokenModel


class JWTToken(JWTTokenModel, table=True):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)
    user_id: int | None = Field(
        default=None, foreign_key="users.id", ondelete="SET NULL"
    )
    user: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})

    @property
    def is_expired(self) -> bool:
        expiration_time = auth_utils.get_token_expire_datetime(self.created_at)
        safety_now_time = datetime.datetime.now(datetime.timezone.utc)
        return expiration_time < safety_now_time

    @property
    def is_valid(self):
        return not self.is_expired

    @property
    def can_be_refreshed(self):
        if self.is_valid:
            return True

        expired_dt = auth_utils.get_token_expire_datetime(self.created_at)
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - expired_dt
        return (delta.seconds / 60) <= settings.TOKEN_REFRESH_DELAY_MINUTES

    @classmethod
    async def _create(cls, user: User):
        dt = auth_utils.get_token_expire_datetime()
        return await cls(
            access_token=cls._generate_jwt_token(user, dt), user=user
        ).save()

    @classmethod
    async def get_or_create(cls, user: User) -> Self:
        token = await cls.get(user_id=user.id)
        if token is not None and not token.is_expired:
            return token

        return await cls._create(user)

    async def refresh(self):
        refresh_delta = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(seconds=1)
        dt = auth_utils.get_token_expire_datetime(refresh_delta)
        data = {
            "access_token": JWTToken._generate_jwt_token(self.user, dt),
            "created_at": dt.replace(tzinfo=None),
        }
        self.update_from_dict(data)
        await self.save()

    @classmethod
    def _generate_jwt_token(cls, user: User, exp: datetime.datetime):
        payload = JWTPayload(sub=user.username, exp=exp)
        return auth_utils.generate_jwt_token(payload)
