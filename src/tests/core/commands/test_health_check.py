from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from core.commands.cli import app as main_app

runner = CliRunner()


def test_command_heath_check_success(httpx_mock: HTTPXMock):
    httpx_mock.add_response(200, json={"status": "ok"})

    result = runner.invoke(main_app, ["healthcheck"])
    assert result.exit_code == 0


def test_command_heath_check_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(400)

    result = runner.invoke(main_app, ["healthcheck"])
    assert result.exit_code == 1
