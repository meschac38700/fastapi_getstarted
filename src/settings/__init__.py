from settings.entity import SettingsDep, get_settings

from .settings import BASE_DIR, DATABASE_ENV_FILE

settings = get_settings()

__all__ = [
    "BASE_DIR",
    "DATABASE_ENV_FILE",
    "settings",
    "SettingsDep",
]
