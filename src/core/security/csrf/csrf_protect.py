from functools import partial
from typing import Any, Callable, Literal, Sequence, cast

from fastapi import UploadFile
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import (
    InvalidHeaderError,
    MissingTokenError,
    TokenValidationError,
)
from fastapi_csrf_protect.load_config import LoadConfig
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from starlette.requests import Request


class LoadConfigFixed(LoadConfig):
    def validate_token_location(self) -> None:
        if self.token_location not in {"body", "header", "header_or_body"}:
            raise TypeError(
                'Field "token_location" must be either "body", "header" or "header_or_body".'
            )


class CsrfProtectFixed(CsrfProtect):
    """Support for CSRF validation in both header and body.
    TODO(Eliam): Remove this class once this PR is merged: https://github.com/aekasitt/fastapi-csrf-protect/pull/29
    """

    def get_csrf_from_form(self, request: Request) -> str | None:
        token = (
            request._json.get(self._token_key, "")
            if hasattr(request, "_json")
            else None
        )

        if not token and hasattr(request, "_form") and request._form is not None:
            form_data: None | UploadFile | str = request._form.get(self._token_key)

            if not form_data or isinstance(form_data, UploadFile):
                raise MissingTokenError("Form data must be of type string")

            token = form_data

        return token

    async def get_csrf_from_request(self, request: Request) -> str | None:
        token = None

        request_body = await request.body()

        extractors = [
            partial(self.get_csrf_from_headers, request.headers),
            partial(self.get_csrf_from_form, request),
            partial(self.get_csrf_from_body, request_body),
        ]

        for extractor in extractors:
            try:
                token = extractor()

                if token:
                    return token

            except (InvalidHeaderError, MissingTokenError, ValidationError):
                continue

        raise MissingTokenError("Token must be provided.")

    async def get_csrf_token(self, request: Request):
        if self._token_location == "header_or_body":
            return await self.get_csrf_from_request(request)

        if self._token_location == "header":
            return self.get_csrf_from_headers(request.headers)

        token = self.get_csrf_from_form(request)

        if token is None:
            token = self.get_csrf_from_body(await request.body())

        return token

    async def validate_csrf(
        self,
        request: Request,
        cookie_key: str | None = None,
        secret_key: str | None = None,
        time_limit: int | None = None,
    ) -> None:
        """
        Check if the given data is a valid CSRF token. This compares the given
        signed token to the one stored in the session.

        ---
        :param request: incoming Request instance
        :type request: fastapi.requests.Request
        :param cookie_key: (Optional) field name for the CSRF token field stored in cookies
            Default is set in CsrfConfig when `load_config` was called;
        :type cookie_key: str
        :param secret_key: (Optional) secret key used to decrypt the token
            Default is set in CsrfConfig when `load_config` was called;
        :type secret_key: str
        :param time_limit: (Optional) Number of seconds that the token is valid.
            Default is set in CsrfConfig when `load_config` was called;
        :type time_limit: int
        :raises TokenValidationError: Contains the reason that validation failed.

        """

        secret_key = secret_key or self._secret_key

        if secret_key is None:
            raise RuntimeError("A secret key is required to use CsrfProtect extension.")

        cookie_key = cookie_key or self._cookie_key

        signed_token = request.cookies.get(cookie_key)

        if signed_token is None:
            raise MissingTokenError(f"Missing Cookie: `{cookie_key}`.")

        token = await self.get_csrf_token(request)

        self._validate_csrf_token(
            token, signed_token, time_limit=time_limit, secret_key=secret_key
        )

    def _validate_csrf_token(
        self,
        token: str,
        signed_token: str,
        *,
        secret_key: str | None = None,
        time_limit: int | None = None,
    ) -> None:
        time_limit = time_limit or self._max_age

        serializer = URLSafeTimedSerializer(secret_key, salt="fastapi-csrf-token")
        try:
            signature: str = serializer.loads(signed_token, max_age=time_limit)
            if token != signature:
                raise TokenValidationError(
                    "The CSRF signatures submitted do not match."
                )
        except SignatureExpired:
            raise TokenValidationError("The CSRF token has expired.")
        except BadData:
            raise TokenValidationError("The CSRF token is invalid.")

    @classmethod
    def load_config(
        cls, settings: Callable[..., Sequence[tuple[str, Any]] | BaseSettings]
    ) -> None:
        try:
            config = LoadConfigFixed(
                **{key.lower(): value for key, value in settings()}
            )
            cls._cookie_key = config.cookie_key or cls._cookie_key
            cls._cookie_path = config.cookie_path or cls._cookie_path
            cls._cookie_domain = config.cookie_domain
            if config.cookie_samesite in {"lax", "none", "strict"}:
                cls._cookie_samesite = cast(
                    Literal["lax", "none", "strict"], config.cookie_samesite
                )
            cls._cookie_secure = (
                False if config.cookie_secure is None else config.cookie_secure
            )
            cls._header_name = config.header_name or cls._header_name
            cls._header_type = config.header_type
            cls._httponly = True if config.httponly is None else config.httponly
            cls._max_age = config.max_age or cls._max_age
            cls._methods = config.methods or cls._methods
            cls._secret_key = config.secret_key
            cls._token_location = config.token_location or cls._token_location
            cls._token_key = config.token_key or cls._token_key
        except ValidationError:
            raise
        except Exception as err:
            print(err)
            raise TypeError(
                'CsrfConfig must be pydantic "BaseSettings" or list of tuple'
            )
