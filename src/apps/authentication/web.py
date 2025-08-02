from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from starlette.responses import RedirectResponse

from apps.authentication.dependencies.oauth2 import current_user
from apps.authentication.models import JWTToken
from apps.authentication.utils import verify_user
from apps.user.dependencies.access import AnonymousUserAccess
from apps.user.models import User
from apps.user.models.schema.create import UserCreate
from core.auth import utils as auth_utils
from core.auth.forms import SessionAuthRequestForm, SessionRegisterRequestForm
from core.security.csrf import csrf_required
from core.templating.utils import render
from settings import settings

routers = APIRouter(tags=["Authentication"], prefix=settings.AUTH_PREFIX_URL)


@routers.get(
    "/session/",
    name="session-login",
    description="Return login HTML page.",
    dependencies=[Depends(AnonymousUserAccess())],
)
async def session_login_view(request: Request):
    return render(request, "authentication/login.html")


@routers.post(
    "/session/",
    name="session-login",
    dependencies=[
        Depends(csrf_required),
        Depends(AnonymousUserAccess()),
    ],
)
async def session_login(
    request: Request, form_data: Annotated[SessionAuthRequestForm, Depends()]
):
    """Login using session auth."""
    user = await verify_user(form_data)
    auth_utils.session_save_user(request, user)
    return RedirectResponse(
        settings.session_auth_redirect_success, status.HTTP_302_FOUND
    )


@routers.post("/logout/", name="session-logout")
async def session_logout(request: Request, auth_user: User = Depends(current_user)):
    request.session.clear()

    token = await JWTToken.get(user=auth_user)
    if token is not None:
        await token.delete()

    return RedirectResponse(request.url_for("session-login"), status.HTTP_302_FOUND)


@routers.get(
    "/session/register/",
    name="session-register",
    description="Return register HTML page.",
    dependencies=[Depends(AnonymousUserAccess())],
)
async def session_register_view(request: Request):
    return render(request, "authentication/register.html")


@routers.post(
    "/session/register/",
    name="session-register",
    dependencies=[Depends(csrf_required), Depends(AnonymousUserAccess())],
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
