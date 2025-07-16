from typing import Any

import jwt
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

from settings import settings


def decode_jwt_token(access_token: str) -> dict[str, Any]:
    return jwt.decode(
        access_token, settings.secret_key, algorithms=[settings.algorithm]
    )


def jwt_token_from_request(request: Request):
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    return scheme, token
