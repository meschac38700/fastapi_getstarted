import logging
import os
import subprocess

import typer

import settings
from core.monitoring.logger import get_logger

app = typer.Typer(rich_markup_mode="rich")
_logger = get_logger(__file__)


class TestRunner:
    def __init__(self, p_logger: logging.Logger | None = None):
        self.logger = p_logger or _logger
        self.env_vars = {
            "APP_ENVIRONMENT": "test",
        }

    @property
    def coverage_options(self):
        return ["--cov=.", "--cov-report=xml", "--cov-fail-under=90"]

    def _run_tests(
        self, test_paths: list[str] | None = None, coverage: bool = False, *pytest_args
    ):
        """Run pytest with the correct environment variables."""
        _test_paths = test_paths or []
        self.logger.info("Start running tests.")

        cov_opts = []
        if coverage:
            cov_opts = self.coverage_options

        ps = subprocess.Popen(
            ["pytest", *pytest_args, *_test_paths] + cov_opts,
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
        coverage: bool = False,
    ):
        if all((test_paths, target_apps)):
            raise ValueError("Cannot specify both 'target_app' and 'test_paths'.")

        _test_paths = test_paths
        if target_apps:
            _test_paths = [
                f"{settings.BASE_DIR / "apps" / app_name}" for app_name in target_apps
            ]

        self._run_tests(_test_paths, coverage=coverage, *pytest_args)
