from functools import lru_cache
from typing import Literal, Optional, Set

from ._base import AppBaseSettings


class CSRFSettings(AppBaseSettings):
    cookie_key: Optional[str] = "fastapi-csrf-token"
    session_cookie: Optional[str] = "session"
    """
    Redirect user after session authentication succeeded.
    """
    session_auth_redirect_success: Optional[str] = "/web/chat/"
    session_user_key: Optional[str] = "user"
    cookie_path: Optional[str] = "/"
    cookie_domain: Optional[str] = None
    """
    All major browsers currently support the following SameSite restriction levels:
        Strict:
            Browsers will not share cookies in any cross-site requests.
        Lax:
            browsers will share cookies in cross-site requests, but only if:
                - Request uses GET method.
                - Request is top-level navigation. (Not initiated by scripts, iframes, loading images etc.)
        None:
            This completely disables SameSite restrictions.
                When setting a cookie with "SameSite=None", the website must also include the "Secure" attribute,
                which ensures that the cookie is only sent in encrypted messages over HTTPS.
                Otherwise, browsers will reject the cookie and it won't be set.

            ex:
                Set-Cookie: cookie_id=0D4ftgOvf4ynV2M9em31dAw; SameSite=None; Secure
    """
    cookie_samesite: Literal["strict", "lax", "none"] = "strict"
    cookie_secure: Optional[bool] = False
    header_name: Optional[str] = None
    header_type: Optional[str] = None
    httponly: Optional[bool] = True
    max_age: Optional[int] = 3600
    methods: Optional[
        Set[Literal["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]]
    ] = None
    secret_key: Optional[str] = None
    token_location: Optional[str] = "body"
    token_key: Optional[str] = "csrf_token"


@lru_cache
def get_csrf_settings():
    return CSRFSettings()
