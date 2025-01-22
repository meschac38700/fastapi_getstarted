from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine

from .constants import DATABASE_ENV_FILE


class Settings(BaseSettings):
    postgres_user: str = "fastapi"
    postgres_password: str = "fastapi"
    postgres_db: str = "fastapi"
    host_db: str = "localhost"
    port_db: int = 5432
    app_environment: Literal["prod", "test", "dev"] = "dev"
    app_port: int = 8000
    model_config = SettingsConfigDict(
        env_file=DATABASE_ENV_FILE, cli_ignore_unknown_args=True
    )
    password_hasher_index: int = 0

    def get_engine(self):
        engine = create_engine(self.uri)
        return engine

    @property
    def uri(self):
        # return f"mysql+pymysql://{self.postgres_user}:{self.postgres_password}@{self.host_db}:{self.port_db}/{self.postgres_db}"
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.host_db}:{self.port_db}/{self.postgres_db}"


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
