import os
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).parent.parent


class AppBaseSettings(BaseSettings):
    """
    Application secret key used in different aspects of the application:
        encode JWT token, generate CSRF token, etc.
    """

    secret_key: str

    BASE_DIR: ClassVar[Path] = _BASE_DIR

    model_config = SettingsConfigDict(
        env_file=_BASE_DIR.parent / "envs" / os.getenv("APP_ENVIRONMENT") / ".env",
        cli_ignore_unknown_args=True,
        extra="allow",
    )
