from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from core.commands.cli import app as main_app

runner = CliRunner()


# NOTE:
#     These tests are redundant and not very interesting,
#     but we'll keep them as examples of tests on typer commands.


def test_command_heath_liveness(httpx_mock: HTTPXMock):
    httpx_mock.add_response(200, json={"status": "OK"})

    result = runner.invoke(main_app, ["healthcheck", "--liveness"])
    assert result.exit_code == 0


def test_command_heath_readiness(httpx_mock: HTTPXMock):
    httpx_mock.add_response(200, json={"status": "OK"})

    result = runner.invoke(main_app, ["healthcheck", "--readiness"])
    assert result.exit_code == 0


def test_command_heath_check_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(400)

    result = runner.invoke(main_app, ["healthcheck"])
    assert result.exit_code == 1
