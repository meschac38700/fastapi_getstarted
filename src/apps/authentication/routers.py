from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from apps.authentication.models import JWTToken
from apps.authentication.models.pydantic import JWTTokenRead
from apps.user.models import User

routers = APIRouter(tags=["authentication"], prefix="/auth")


@routers.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JWTTokenRead:
    user = await User.get(User.username == form_data.username)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    valid_password = user.check_password(form_data.password)
    if not valid_password:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect username or password"
        )
    token = await JWTToken.get_or_create(user)
    return JWTTokenRead.model_validate(token)
