import re

from fastapi import FastAPI, status

from core.templating.utils import render_string
from core.unittest.client import AsyncClientTest


async def test_get_session_login_form(
    client: AsyncClientTest, app: FastAPI, http_request
):
    response = await client.get(app.url_path_for("session-login"))
    assert response.status_code == status.HTTP_200_OK
    html_response = response.content.decode()
    expected_html = render_string(http_request, "authentication/login.html")

    # bypass csrf_token
    html_response = re.sub(
        re.compile(r'name="csrf_token" value="\w+"'),
        'name="csrf_token" value="None"',
        html_response,
    )

    assert expected_html == html_response
