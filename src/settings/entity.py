from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import DATABASE_ENV_FILE


class Settings(BaseSettings):
    server_address: str = "http://127.0.0.1"
    postgres_user: str = "fastapi"
    postgres_password: str = "fastapi"
    postgres_db: str = "fastapi"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    app_environment: Literal["prod", "test", "dev"] = "dev"
    app_port: int = 8000
    model_config = SettingsConfigDict(
        env_file=DATABASE_ENV_FILE, cli_ignore_unknown_args=True, extra="allow"
    )
    password_hasher_index: int = 0
    secret_key: str = ""
    algorithm: str = "HS256"

    # sentry config
    sentry_dsn: str = ""
    sentry_send_pii: bool = False

    # Celery
    celery_broker: str = ""
    celery_backend: str = ""
    """
    Source: https://ankurdhuriya.medium.com/understanding-celery-workers-concurrency-prefetching-and-heartbeats-85707f28c506
    Concurrency refers to the ability of a worker to handle multiple tasks at the same time.
    By default, Celery workers use a concurrency level of one, which means that each worker can only handle one task at a time.
    However, this can be increased to handle multiple tasks simultaneously.
    """
    celery_task_concurrency: int = 1
    """
    Prefetching is the process of loading a batch of tasks into a worker’s memory before they are actually executed.
    This can help to improve performance by reducing the time it takes to fetch new tasks from the broker.
    """
    celery_prefetch_multiplier: int = 1
    """
    Heartbeats are a way for Celery workers to communicate with the broker and ensure that they are still alive.
    Workers send periodic heartbeat messages to the broker to let it know that they are still running.
    """
    celery_worker_heartbeat: int = 120  # Send a heartbeat every 120 seconds by default

    # CORS authorization
    cors_allowed_origins: list[str] = []
    cors_allowed_headers: list[str] = ["*"]
    cors_allowed_methods: list[str] = ["*"]

    @property
    def uri(self):
        prefix = "postgresql+asyncpg://"
        db = self.postgres_db
        port = self.postgres_port
        host = self.postgres_host
        return (
            f"{prefix}{self.postgres_user}:{self.postgres_password}@{host}:{port}/{db}"
        )

    @property
    def health_check_endpoint(self):
        return f"{self.server_address}:{self.app_port}/healthcheck"

    @property
    def health_check_endpoint(self):
        return f"{self.server_address}:{self.app_port}/healthcheck"


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
