import asyncio
import re
from logging.config import fileConfig
from typing import Any, Sequence

import sqlalchemy as sa
from alembic import context
from sqlalchemy import pool
from sqlalchemy.dialects.postgresql.asyncpg import PGExecutionContext_asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from apps import app_metadata
from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.authorization.models.relation_links import PermissionGroupLink
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


def sql_select(
    conn, table_name: str, *, where: str, order_by: str = ""
) -> list[dict[str, Any]]:
    perms_statement = sa.text(f"""
        SELECT *
        FROM {table_name}
        WHERE {where}
        {order_by};
    """)
    return conn.execute(perms_statement).mappings().all()


async def link_permission_to_group(
    perms: Sequence[Permission], groups: Sequence[Group]
):
    task_list = []
    for perm in perms:
        for group in groups:
            if group.name != perm.name:
                continue
            group.permissions = [*group.permissions, perm]
            task_list.append(group.save())

    await asyncio.gather(*task_list)


async def generate_old_models_crud_permissions(engine: Any):
    """Generate CRUD permissions for all created models before permission model.

    (User/Hero models)
    """

    def permission_table_exists(conn):
        return conn.engine.dialect.has_table(conn, "permission")

    if not await engine.run_sync(permission_table_exists):
        return

    await asyncio.gather(
        Permission.generate_crud_objects("hero"),
        Permission.generate_crud_objects("user"),
        Group.generate_crud_objects("hero"),
        Group.generate_crud_objects("user"),
    )
    perms_user, perms_hero, groups_user, groups_hero = await asyncio.gather(
        Permission.filter(Permission.target_table == "user"),
        Permission.filter(Permission.target_table == "hero"),
        Group.filter(Permission.target_table == "user"),
        Group.filter(Permission.target_table == "hero"),
    )
    await asyncio.gather(
        link_permission_to_group(perms_user, groups_user),
        link_permission_to_group(perms_hero, groups_hero),
    )


async def run_async_migrations(connectable):
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await generate_old_models_crud_permissions(connection)
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


Data = list[dict[str, Any]]


def _get_permission_group_link_insert_query(permissions: Data, groups: Data) -> str:
    query = f"""
    INSERT INTO {PermissionGroupLink.table_name()}(permission_name, group_name) VALUES
    """
    for i, perm_group in enumerate(zip(permissions, groups)):
        perm, group = perm_group
        val = (perm["name"], group["name"])
        if i > 0:
            query += f",\n {val}"
            continue
        query += f"{val}"
    return query + ";"


def after_cursor_execute(
    conn, cursor, statement, _, context: PGExecutionContext_asyncpg, ___
):
    if not context.isddl:
        return

    table_name = _extract_table_name(statement)

    permission_table_exists = conn.engine.dialect.has_table(
        conn, Permission.table_name()
    )
    if not permission_table_exists or table_name is None:
        return

    # Auto generate crud permissions for previously created model table
    perms_sql = Permission.get_crud_data_list(table_name, raw_sql=True)
    cursor.execute(perms_sql)
    perms = sql_select(
        conn,
        Permission.table_name(),
        where=f"target_table='{table_name}'",
        order_by="ORDER BY name",
    )

    # Auto generate crud groups for previously created model table
    table_exists = conn.engine.dialect.has_table(conn, Group.table_name())
    if not table_exists:
        return
    groups_sql = Group.get_crud_data_list(table_name, raw_sql=True)
    cursor.execute(groups_sql)
    groups = sql_select(
        conn,
        Group.table_name(),
        where=f"name LIKE '%_{table_name}'",
        order_by="ORDER BY name",
    )

    # permission group link
    table_exists = conn.engine.dialect.has_table(conn, PermissionGroupLink.table_name())
    if not table_exists:
        return
    permission_group_link_sql = _get_permission_group_link_insert_query(perms, groups)
    cursor.execute(permission_group_link_sql)


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
