import logging
import os
import subprocess

import typer

import settings

app = typer.Typer(rich_markup_mode="rich")
_logger = logging.getLogger(__file__)


class TestRunner:
    def __init__(self, p_logger: logging.Logger | None = None):
        self.logger = p_logger or _logger
        self.env_vars = {
            "APP_ENVIRONMENT": "test",
        }

    def _run_tests(self, test_paths: list[str] | None = None, *pytest_args):
        """Run pytest with the correct environment variables."""
        _test_paths = test_paths or []
        self.logger.info("Start running tests.")
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
    ):
        if all((test_paths, target_apps)):
            raise ValueError("Cannot specify both 'target_app' and 'test_paths'.")

        _test_paths = [str(test_path) for test_path in test_paths]
        if target_apps:
            _test_paths = [
                f"{settings.BASE_DIR / "apps" / app_name}" for app_name in target_apps
            ]

        self._run_tests(_test_paths, *pytest_args)
