from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine

from settings.generic import DATABASE_ENV_FILE


class DatabaseSettings(BaseSettings):
    postgres_user: str = "fastapi"
    postgres_password: str = "fastapi"
    postgres_db: str = "fastapi"
    host: str = "localhost"
    port: int = 5432
    model_config = SettingsConfigDict(env_file=DATABASE_ENV_FILE)

    def get_engine(self):
        return create_engine(self.uri)

    @property
    def uri(self):
        breakpoint()
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.host}:{self.port}/{self.postgres_db}"


@lru_cache
def get_settings():
    return DatabaseSettings()


DBSettingsDep = Annotated[DatabaseSettings, Depends(get_settings)]
