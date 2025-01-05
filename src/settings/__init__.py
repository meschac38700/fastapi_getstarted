from settings.database import DatabaseSettings, DBSettingsDep, get_settings

from .settings import BASE_DIR, DATABASE_ENV_FILE

db_settings = get_settings()

__all__ = [
    "BASE_DIR",
    "DATABASE_ENV_FILE",
    "db_settings",
    "DatabaseSettings",
    "DBSettingsDep",
]
