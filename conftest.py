import uuid

import pytest
from celery import current_app
from sqlalchemy.ext.asyncio import AsyncEngine

from core.db import create_all_tables, delete_all_tables
from core.db.dependencies.session import get_engine
from core.db.utils import (
    create_database_if_not_exists,
    drop_database_if_exists,
)


def update_settings(database: str, settings):
    uri = settings.uri.replace("postgresql+asyncpg://", "postgresql://", 1)
    if getattr(settings, "_admin_uri", None) is None:
        settings._admin_uri = uri
    settings.postgres_db = database


@pytest.fixture
def settings():
    from settings import settings

    return settings


@pytest.fixture
def db_name(request, worker_id):
    method_name = request.node.name
    _uuid = uuid.uuid4().hex[:6]
    db_name = f"{_uuid}_{method_name[:50]}_{worker_id}"
    return db_name


@pytest.fixture(autouse=True, scope="function")
def enable_celery_eager():
    current_app.conf.task_always_eager = True
    current_app.conf.task_eager_propagates = True


@pytest.fixture(scope="function")
async def db(db_name, settings):
    update_settings(db_name, settings)
    await create_database_if_not_exists(db_name, getattr(settings, "_admin_uri", None))
    _engine: AsyncEngine = get_engine()
    await create_all_tables(_engine)
    yield _engine
    await delete_all_tables(_engine)
    await drop_database_if_exists(db_name, settings._admin_uri)
    await _engine.dispose()
