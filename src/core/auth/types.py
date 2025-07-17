import datetime

from pydantic import BaseModel, Field

from settings import settings


class JWTPayload(BaseModel):
    """JWT payload, keep it simple for now.

    Refer to the 'generate_jwt_token' function in the core.auth.utils.py module.
    """

    exp: datetime.datetime
    sub: str
    iss: str = Field(default=settings.server_address)
