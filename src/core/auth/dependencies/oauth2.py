from fastapi.security import OAuth2PasswordBearer


def oauth2_scheme():
    return OAuth2PasswordBearer(tokenUrl="token")
