from settings.entity import SettingsDep, get_settings

from .constants import (
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
]
