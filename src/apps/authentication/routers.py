from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

from apps.authentication.dependencies import oauth2_scheme
from apps.authentication.models import JWTToken
from apps.authentication.models.schema import JWTTokenRead
from apps.user.models import User
from apps.user.models.schema.create import UserCreate
from core.auth import utils as auth_utils
from core.auth.forms import SessionAuthRequestForm, SessionRegisterRequestForm
from core.security.csrf import csrf_required
from core.templating.utils import render
from settings import settings

routers = APIRouter(tags=["Authentication"], prefix=settings.AUTH_PREFIX_URL)


async def verify_user(
    form_data: OAuth2PasswordRequestForm | SessionAuthRequestForm,
) -> User:
    user = await User.get(username=form_data.username)
    if user is None:
        detail = "Authentication error: user not found."
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)

    valid_password = user.check_password(form_data.password)
    if not valid_password:
        detail = "Authentication error: credentials are invalid."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)
    return user


@routers.post("/token", name="Generate JWT Token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JWTTokenRead:
    user = await verify_user(form_data)
    token = await JWTToken.get_or_create(user)
    return JWTTokenRead.model_validate(token)


@routers.post(
    "/token/refresh", name="Refresh JWT token", dependencies=[Depends(oauth2_scheme())]
)
async def refresh(token: JWTToken = Depends(oauth2_scheme())):
    await token.refresh()
    return JWTTokenRead.model_validate(token)


@routers.get("/session/", name="session-login", description="Return login HTML page.")
async def session_login_view(request: Request):
    return render(request, "authentication/login.html")


@routers.post("/session/", name="session-login", dependencies=[Depends(csrf_required)])
async def session_login(
    request: Request, form_data: Annotated[SessionAuthRequestForm, Depends()]
):
    """Login using session auth."""
    user = await verify_user(form_data)
    auth_utils.session_save_user(request, user)
    return RedirectResponse(
        settings.session_auth_redirect_success, status.HTTP_302_FOUND
    )


@routers.post(
    "/logout/", name="session-logout", dependencies=[Depends(oauth2_scheme())]
)
async def session_logout(request: Request, token: JWTToken = Depends(oauth2_scheme())):
    request.session.clear()
    await token.delete()
    return RedirectResponse(request.url_for("session-login"), status.HTTP_302_FOUND)


@routers.get(
    "/session/register/",
    name="session-register",
    description="Return register HTML page.",
)
async def session_register_view(request: Request):
    return render(request, "authentication/register.html")


@routers.post(
    "/session/register/", name="session-register", dependencies=[Depends(csrf_required)]
)
async def session_register(
    request: Request, user_data: Annotated[SessionRegisterRequestForm, Depends()]
):
    valid_user_data = UserCreate.model_validate(user_data.to_dict())
    user = await User(**valid_user_data.model_dump()).save()
    auth_utils.session_save_user(request, user)
    return RedirectResponse(
        settings.session_auth_redirect_success, status.HTTP_302_FOUND
    )
