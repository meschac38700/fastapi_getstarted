from settings.entity import SettingsDep, get_settings

from .constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_PREFIX_URL,
    AUTH_URL,
    BASE_DIR,
    DATABASE_ENV_FILE,
    PASSWORD_HASHER,
    initial_fixtures,
)

settings = get_settings()

__all__ = [
    "BASE_DIR",
    "DATABASE_ENV_FILE",
    "settings",
    "SettingsDep",
    "PASSWORD_HASHER",
    "initial_fixtures",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "AUTH_PREFIX_URL",
    "AUTH_URL",
]
