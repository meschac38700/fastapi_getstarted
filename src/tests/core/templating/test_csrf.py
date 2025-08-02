from pathlib import Path

from fastapi import status

from core.unittest.client import AsyncClientTest


async def test_generate_csrf_token_on_rendering_html_template(
    client: AsyncClientTest, template_dir: Path, setup_test_routes, serializer
):
    index_file = template_dir / "index.html"
    index_file.write_text("{{csrf_token}}")
    response = await client.get(setup_test_routes)

    assert response.status_code == status.HTTP_200_OK
    token = response.text

    signed_token = response.headers.get("Set-cookie").split(";")[0].split("=")[1]
    unsigned_token = serializer.loads(signed_token, max_age=3600)

    assert unsigned_token == token


async def test_validate_csrf_token_error_token_missing(
    client: AsyncClientTest, setup_test_routes
):
    response = await client.post(setup_test_routes)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.text == "Missing Cookie: `fastapi-csrf-token`."


async def test_validate_csrf_token(
    client: AsyncClientTest, template_dir: Path, setup_test_routes, settings
):
    index_file = template_dir / "index.html"
    index_file.write_text("{{csrf_token}}")

    response = await client.get(setup_test_routes)
    token = response.text

    # make a POST request with csrf a valid token
    token_header = {settings.token_key: token}
    response = await client.post(setup_test_routes, data=token_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "OK"}
