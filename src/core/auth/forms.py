from typing import Annotated

from fastapi.params import Form
from typing_extensions import Doc


class SessionAuthRequestForm:
    def __init__(
        self,
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                `username` string.
                """
            ),
        ],
        password: Annotated[
            str,
            Form(json_schema_extra={"format": "password"}),
            Doc(
                """
                `password` string.
                """
            ),
        ],
    ):
        self.username = username
        self.password = password


class SessionRegisterRequestForm:
    def __init__(
        self,
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                `username` string.
                """
            ),
        ],
        password: Annotated[
            str,
            Form(json_schema_extra={"format": "password"}),
            Doc(
                """
                `password` string.
                """
            ),
        ],
        first_name: Annotated[
            str,
            Form(),
            Doc(
                """
                `first_name` string.
                """
            ),
        ],
        last_name: Annotated[
            str,
            Form(),
            Doc(
                """
                `last_name` string.
                """
            ),
        ],
        email: Annotated[
            str | None,
            Form(),
            Doc(
                """
                `first_name` string.
                """
            ),
        ] = None,
    ):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def to_dict(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
        }


class CSRFTokenRequestForm:
    def __init__(
        self,
        csrf_token: Annotated[
            str | None,
            Form(),
            Doc(
                """
                `csrf_token` string.
                """
            ),
        ] = None,
    ):
        self.csrf_token = csrf_token
