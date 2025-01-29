from fastapi.security import OAuth2PasswordBearer

import settings


def oauth2_scheme():
    return OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)
