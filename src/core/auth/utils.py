import datetime

import jwt
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

from core.auth.types import JWTPayload
from settings import settings


def generate_jwt_token(token_data: JWTPayload) -> str:
    _token_data = token_data.model_dump()
    return jwt.encode(_token_data, settings.secret_key, algorithm=settings.algorithm)


def decode_jwt_token(access_token: str) -> JWTPayload:
    return JWTPayload(
        **jwt.decode(access_token, settings.secret_key, algorithms=[settings.algorithm])
    )


def decode_jwt_token_from_request(request: Request):
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    return scheme, token


def get_token_expire_datetime(created_at: datetime.datetime | None = None):
    start_dt = created_at or datetime.datetime.now(datetime.timezone.utc)
    dt = start_dt + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return dt.replace(tzinfo=datetime.timezone.utc)
