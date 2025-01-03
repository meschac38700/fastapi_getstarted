from .postgres_configs import DatabaseSettings, DBSettingsDep, get_settings

db_settings = get_settings()

__all__ = [
    "db_settings",
    "DatabaseSettings",
    "DBSettingsDep",
]
