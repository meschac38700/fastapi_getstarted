from pydantic_settings import BaseSettings

from .generic import BASE_DIR


class DatabaseSettings(BaseSettings):
    _env_prefix = "db"
    _env_file = BASE_DIR.parent / "envs" / ".db.env"
    user: str = "fastapi"
    password: str = "fastapi"
    host: str = "database"
    name: str = "fastapi"
