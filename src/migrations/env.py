import asyncio
import re
from logging.config import fileConfig
from typing import Any

import sqlalchemy as sa
from alembic import context
from sqlalchemy import pool
from sqlalchemy.dialects.postgresql.asyncpg import PGExecutionContext_asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from apps import app_metadata
from migrations.events.after_cursor_execute import ManagePermissionMigration
from settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = app_metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

Data = list[dict[str, Any]]


async def run_async_migrations(connectable):
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _extract_table_name(statement: str) -> str | None:
    pattern = r'CREATE\s+TABLE\s+"?(?P<table_name>\w+)"?'
    res = re.search(pattern, statement, re.IGNORECASE)

    if res is None:
        return None

    return res.group("table_name")


def after_cursor_execute(
    conn, cursor, statement, _, context: PGExecutionContext_asyncpg, ___
):
    if not context.isddl:
        return

    table_name = _extract_table_name(statement)
    permission_manager = ManagePermissionMigration(conn, cursor)

    if not permission_manager.permission_table_exists() or table_name is None:
        return
    perms = permission_manager.generate_permissions(table_name)

    if not permission_manager.group_table_exists():
        return
    groups = permission_manager.generate_groups(table_name)

    permission_manager.generate_permission_group_links(
        table_name, perms=perms, groups=groups
    )


def run_migrations_online():
    ini_section = context.config.get_section(config.config_ini_section)
    ini_section["sqlalchemy.url"] = settings.uri
    connectable = async_engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    sa.event.listens_for(connectable.sync_engine, "after_cursor_execute")(
        after_cursor_execute
    )

    if isinstance(connectable, AsyncEngine):
        asyncio.run(run_async_migrations(connectable))
    else:
        do_run_migrations(connectable)


run_migrations_online()
