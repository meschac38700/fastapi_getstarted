from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import settings
from apps.authentication.dependencies import oauth2_scheme
from apps.authentication.models import JWTToken
from apps.authentication.models.pydantic import JWTTokenRead
from apps.user.models import User

routers = APIRouter(tags=["Authentication"], prefix=settings.AUTH_PREFIX_URL)


@routers.post("/token", name="Generate JWT Token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JWTTokenRead:
    user = await User.get(username=form_data.username)
    if user is None:
        detail = "Authentication error: user not found."
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)

    valid_password = user.check_password(form_data.password)
    if not valid_password:
        detail = "Authentication error: credentials are invalid."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)
    token = await JWTToken.get_or_create(user)
    return JWTTokenRead.model_validate(token)


@routers.post(
    "/token/refresh", name="Refresh JWT token", dependencies=[Depends(oauth2_scheme())]
)
async def refresh(token: JWTToken = Depends(oauth2_scheme())):
    await token.refresh()
    return JWTTokenRead.model_validate(token)
