from copy import deepcopy
from typing import Any, Optional, TypeVar

import asyncpg
import pydantic_core
from alembic import command
from alembic.config import Config
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

import settings
from core.monitoring.logger import get_logger

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)

logger = get_logger(__name__)


async def create_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()


async def delete_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


async def database_exists(db_name, admin_url):
    conn = await asyncpg.connect(admin_url)
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", db_name
    )
    return exists


async def create_database_if_not_exists(db_name, admin_url):
    conn = await asyncpg.connect(admin_url)
    exists = await database_exists(db_name, admin_url)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
    await conn.close()


def run_alembic_upgrade(
    revision: str = "head",
    alembic_ini_path: str = str(settings.BASE_DIR / "alembic.ini"),
):
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, revision)


async def drop_database_if_exists(db_name, admin_url):
    conn = await asyncpg.connect(admin_url)
    exists = await database_exists(db_name, admin_url)
    if exists:
        await conn.execute(f'DROP DATABASE "{db_name}"')
    await conn.close()


# Context: https://github.com/pydantic/pydantic/issues/3120#issuecomment-1528030416


def optional_fields(model: type[BaseModelT]) -> type[BaseModelT]:
    def make_field_optional(
        field: FieldInfo, default: Any = None
    ) -> tuple[Any, FieldInfo]:
        new = deepcopy(field)
        if not isinstance(field.default, pydantic_core.PydanticUndefinedType):
            new.default = field.default
        else:
            new.default = default
        new.annotation = Optional[field.annotation]
        return new.annotation, new

    return create_model(
        f"Partial{model.__name__}",
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        },
    )
