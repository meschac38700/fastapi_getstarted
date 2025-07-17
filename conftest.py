import shutil
import uuid
from pathlib import Path
from unittest.mock import patch

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
def app():
    from main import app as main_app

    return main_app


@pytest.fixture
async def client(app):
    from httpx import ASGITransport

    from core.unittest.client import AsyncClientTest

    client = AsyncClientTest(transport=ASGITransport(app=app), base_url="https://test")
    yield client
    await client.aclose()


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


@pytest.fixture(scope="function")
def http_request():
    from fastapi import Request

    return Request(scope={"type": "http"})


@pytest.fixture(scope="function")
def websocket_request():
    from fastapi import Request

    return Request(scope={"type": "websocket"})


@pytest.fixture
def template_dir():
    """Mock the app directory to create fake templates for testing purposes."""
    from core.templating.loaders import app_template_loader

    app_dir = Path(__file__).parent / "tests" / "core" / "templating"
    with patch("core.templating.loaders.apps.file_services") as mock_file_services:
        mock_file_services.get_application_paths.return_value = [app_dir]
        template_dir = app_dir / app_template_loader.loader.template_dirname
        template_dir.mkdir(parents=True, exist_ok=True)
        yield template_dir

    # clear test data
    shutil.rmtree(str(template_dir), ignore_errors=True)
