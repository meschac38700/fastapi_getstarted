from pathlib import Path

import pytest
from fastapi import Depends, status
from itsdangerous import URLSafeTimedSerializer

from core.security.csrf import csrf_required
from core.unittest.client import AsyncClientTest

_GET = "/azeaze/"
_POST = "/azeaze/create/"


@pytest.fixture()
def serializer(settings):
    return URLSafeTimedSerializer(settings.secret_key, salt="fastapi-csrf-token")


@pytest.fixture(autouse=True)
def csrf_app_setup(app):
    """
    Sets up some FastAPI endpoints for test purposes.
    """
    from fastapi import Request
    from fastapi.responses import HTMLResponse, JSONResponse

    from core.templating.utils import render

    @app.get(_GET, response_class=HTMLResponse)
    async def read(request: Request) -> HTMLResponse:
        # generate token
        return render(request, "index.html")

    # use csrf_required Depends to validate csrf token
    @app.post(_POST, response_class=JSONResponse)
    async def create(_=Depends(csrf_required)) -> JSONResponse:
        return JSONResponse(status_code=200, content={"detail": "OK"})


async def test_generate_csrf_token_on_rendering_html_template(
    client: AsyncClientTest, template_dir: Path, serializer
):
    index_file = template_dir / "index.html"
    index_file.write_text("{{csrf_token}}")
    response = await client.get(_GET)

    assert response.status_code == status.HTTP_200_OK
    token = response.text

    signed_token = response.headers.get("Set-cookie").split(";")[0].split("=")[1]
    unsigned_token = serializer.loads(signed_token, max_age=3600)

    assert unsigned_token == token


async def test_validate_csrf_token_error_token_missing(client: AsyncClientTest):
    response = await client.post(_POST)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.text == "Missing Cookie: `fastapi-csrf-token`."


async def test_validate_csrf_token(
    client: AsyncClientTest, template_dir: Path, settings
):
    index_file = template_dir / "index.html"
    index_file.write_text("{{csrf_token}}")

    response = await client.get(_GET)
    token = response.text

    # make a POST request with csrf a valid token
    token_header = {settings.header_name: token}
    response = await client.post(_POST, headers=token_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "OK"}
