from http import HTTPStatus

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from apps.user.models import User
from core.auth.forms import SessionAuthRequestForm


async def verify_user(
    form_data: OAuth2PasswordRequestForm | SessionAuthRequestForm,
) -> User:
    """Verify user credentials."""
    user = await User.get(username=form_data.username)
    if user is None:
        detail = "Authentication error: user not found."
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)

    valid_password = user.check_password(form_data.password)
    if not valid_password:
        detail = "Authentication error: credentials are invalid."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)
    return user
