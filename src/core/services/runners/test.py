import logging
import os
import subprocess

import typer

from core.monitoring.logger import get_logger
from settings import settings

app = typer.Typer(rich_markup_mode="rich")
_logger = get_logger(__file__)


class AppTestRunner:
    def __init__(self, p_logger: logging.Logger | None = None):
        self.logger = p_logger or _logger
        self.env_vars = {
            "APP_ENVIRONMENT": "test",
        }

    def _prepare_test_environment(self):
        scripts_path = settings.BASE_DIR / "scripts" / "prepare_tests.sh"
        ps = subprocess.Popen(
            ["sh", scripts_path],
            env=dict(os.environ, **self.env_vars),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if ps.returncode != 0:
            self.logger.exception("Migrations already applied.")

    def _run_tests(self, test_paths: list[str] | None = None, *pytest_args):
        """Run pytest with the correct environment variables."""
        _test_paths = test_paths or []
        self.logger.info("Start running tests.")

        self._prepare_test_environment()
        ps = subprocess.Popen(
            ["pytest", *pytest_args, *_test_paths],
            env=dict(os.environ, **self.env_vars),
            stderr=subprocess.STDOUT,
        )
        return ps.wait()

    def __call__(
        self,
        *,
        target_apps: list[str],
        pytest_args: list[str],
        test_paths: list[str] | None = None,
        e2e: bool = False,
    ):
        e2e_marker_options = ["-m not E2E"]
        if e2e:
            self.logger.info("Preparing to run e2e tests.")
            e2e_marker_options = ["-m E2E"]

        if all((test_paths, target_apps)):
            raise ValueError("Cannot specify both 'target_app' and 'test_paths'.")

        pytest_args = list(set(pytest_args + e2e_marker_options))

        _test_paths = test_paths
        if target_apps:
            _test_paths = [
                f"{settings.BASE_DIR / "apps" / app_name}" for app_name in target_apps
            ]

        self._run_tests(_test_paths, *pytest_args)
