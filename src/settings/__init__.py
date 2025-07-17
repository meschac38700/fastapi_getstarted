from settings.app import SettingsDep, get_settings

settings = get_settings()

__all__ = [
    "settings",
    "SettingsDep",
]
