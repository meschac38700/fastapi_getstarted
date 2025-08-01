import contextlib
import shutil
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from celery import current_app
from fastapi_pagination import add_pagination
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncEngine

from apps.user.utils.types import UserRole
from core.db import create_all_tables, delete_all_tables
from core.db.dependencies.session import get_engine
from core.db.utils import (
    create_database_if_not_exists,
    drop_database_if_exists,
)
from core.services.files import linux_path_to_module_path


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

    add_pagination(main_app)

    return main_app


@pytest.fixture
def base_url(settings):
    return settings.TEST_BASE_URL


@pytest.fixture
async def client(app, base_url):
    from httpx import ASGITransport

    from core.unittest.client import AsyncClientTest

    client = AsyncClientTest(transport=ASGITransport(app=app), base_url=base_url)
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


@pytest.fixture
async def admin(db):  # pylint: disable=unused-argument
    from apps.user.models import User

    return await User(
        username="j.admin",
        first_name="John",
        last_name="Admin",
        email="john.admin@example.org",
        password=(lambda: "admin")(),
        role=UserRole.admin,
    ).save()


@pytest.fixture
async def user(db):  # pylint: disable=unused-argument
    from apps.user.models import User

    return await User(
        username="j.smith",
        first_name="John",
        last_name="Smith",
        email="john.smith@example.org",
        password=(lambda: "password")(),
    ).save()


@pytest.fixture
def url_for(app, base_url):
    def _url_for(endpoint, **kwargs):
        return base_url + app.url_path_for(endpoint, **kwargs)

    return _url_for


@pytest.fixture(scope="function")
def http_request(url_for):
    from fastapi import Request

    request = Request(scope={"type": "http"})
    request.url_for = url_for
    return request


@pytest.fixture(scope="function")
def websocket_request():
    from fastapi import Request

    return Request(scope={"type": "websocket"})


@contextlib.contextmanager
def mock_get_application_paths(mock_service: str, request):
    test_name = request.node.name
    app_dir = Path(request.node.module.__file__).parent / test_name
    app_dir.mkdir(parents=True, exist_ok=True)
    with patch(mock_service) as mock_file_services:
        yield app_dir, mock_file_services

    def _cleanup():
        """Cleanup tests files."""
        shutil.rmtree(app_dir, ignore_errors=True)

    request.addfinalizer(_cleanup)


@pytest.fixture
def template_dir(request):
    """Mock the app directory to create fake templates for testing purposes."""
    from core.templating.loaders import app_template_loader

    with mock_get_application_paths(
        "core.templating.loaders.apps.file_services", request
    ) as (app_dir, mock_obj):
        mock_obj.get_application_paths.return_value = [app_dir]
        template_dir = app_dir / app_template_loader.loader.template_dirname
        template_dir.mkdir(parents=True, exist_ok=True)
        yield template_dir


@pytest.fixture
def static_root(settings, request):
    with mock_get_application_paths("main.file_apps", request) as (app_dir, mock_obj):
        static_root = app_dir / settings.STATIC_ROOT
        static_root.mkdir(parents=True, exist_ok=True)

        mock_obj.static_packages.return_value = [linux_path_to_module_path(app_dir)]

        yield static_root


@pytest.fixture()
def serializer(settings):
    return URLSafeTimedSerializer(settings.secret_key, salt="fastapi-csrf-token")


@pytest.fixture()
def setup_test_routes(app, request):
    """
    Sets up some FastAPI endpoints for test purposes.
    """
    from fastapi import Depends, Request
    from fastapi.responses import HTMLResponse, JSONResponse

    from core.security.csrf import csrf_required
    from core.templating.utils import render

    endpoint = "/test/" + request.node.name + "/"

    @app.get(endpoint, response_class=HTMLResponse)
    async def read(req: Request) -> HTMLResponse:
        # generate token
        return render(req, "index.html")

    # use csrf_required Depends to validate csrf token
    @app.post(endpoint, response_class=JSONResponse)
    async def create(_=Depends(csrf_required)) -> JSONResponse:
        return JSONResponse(status_code=200, content={"detail": "OK"})

    return endpoint


@pytest.fixture
async def csrf_token(serializer, client, app):
    """Mock csrf token for testing purposes."""
    from fastapi import status
    from fastapi_csrf_protect import CsrfProtect

    token = "unsigned_token"

    class CSRFProtect(CsrfProtect):
        def generate_csrf_tokens(self, _: str | None = None):
            signed_token = serializer.dumps(token)
            return (token, signed_token)

    with patch(
        "core.templating.utils.get_csrf_protect", side_effect=CSRFProtect
    ) as mock_csrf_protect:
        # First get request to generate the csrf token which is mocked to a constant value
        response = await client.get(app.url_path_for("session-login"))
        assert response.status_code == status.HTTP_200_OK

        yield token
        mock_csrf_protect.assert_called()
