import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from core.commands.cli import app

runner = CliRunner()


@pytest.mark.asyncio
def test_command_heath_check_success(httpx_mock: HTTPXMock):
    httpx_mock.add_response(200, json={"status": "ok"})

    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 0


@pytest.mark.asyncio
def test_command_heath_check_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(400)

    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 1
