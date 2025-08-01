from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.authentication.dependencies import oauth2_scheme
from apps.authentication.models import JWTToken
from apps.authentication.models.schema import JWTTokenRead
from apps.authentication.utils import verify_user
from settings import settings

routers = APIRouter(tags=["Authentication"], prefix=settings.AUTH_PREFIX_URL)


@routers.post("/token/", name="Generate JWT Token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JWTTokenRead:
    user = await verify_user(form_data)
    token = await JWTToken.get_or_create(user)
    return JWTTokenRead.model_validate(token)


@routers.post(
    "/token/refresh/", name="Refresh JWT token", dependencies=[Depends(oauth2_scheme())]
)
async def refresh(token: JWTToken = Depends(oauth2_scheme())):
    await token.refresh()
    return JWTTokenRead.model_validate(token)
