import logging
from pathlib import Path

import typer

import settings
from core.services.docker.compose import DockerComposeManager
from core.test.runner import AppTestRunner
from core.types.annotations.command_types import (
    TyperListArgument,
    TyperListOption,
)

app = typer.Typer(rich_markup_mode="rich")
_logger = logging.getLogger(__file__)

AppsType = TyperListOption(
    description="Specify an application name on which to run tests."
)
PytestArgsType = TyperListOption(
    "List of arguments to pass to the pytest module in string format."
)
TestPathsType = TyperListArgument(
    'Test paths to run, run all application tests by default. cannot be combined with the "app" option.',
    of_type=Path,
)


@app.command(help="Run application tests.")
def tests(
    apps: AppsType,
    pytest_args: PytestArgsType,
    test_paths: TestPathsType = None,
):
    """Execute application tests.

    usages:
        > python manage.py tests  # Run all application tests
        > python manage.py tests --apps user authentication  # Run all specific application's tests
        > python manage.py tests /apps/user apps/authentication  # Run all tests of the specified applications
        > python manage.py tests --pytest-args --create-db --pytest-args --strict # Specify pytest args
    """
    dk_compose = DockerComposeManager(
        settings.BASE_DIR.parent / "docker-compose.test.yaml", env="test"
    )

    test_command = AppTestRunner()

    def _run_test():
        test_command(
            target_apps=apps, test_paths=test_paths or [], pytest_args=pytest_args
        )

    dk_compose.run_process(_run_test, stop_after=True, force_recreate=True)
