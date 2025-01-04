from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine

from settings.generic import DATABASE_ENV_FILE


class DatabaseSettings(BaseSettings):
    _env_file = DATABASE_ENV_FILE
    _env_prefix = "db"
    postgres_user: str = "fastapi"
    postgres_password: str = "fastapi"
    postgres_db: str = "fastapi"
    host_db: str = "localhost"
    port_db: int = 5432
    model_config = SettingsConfigDict(env_file=DATABASE_ENV_FILE)

    def get_engine(self):
        engine = create_async_engine(self.uri)
        return engine

    @property
    def uri(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.host_db}:{self.port_db}/{self.postgres_db}"


@lru_cache
def get_settings():
    return DatabaseSettings()


DBSettingsDep = Annotated[DatabaseSettings, Depends(get_settings)]
