import typer

from core.monitoring.logger import get_logger
from core.services.docker.compose import DockerComposeRunner
from core.services.runners import AppTestRunner
from core.types.annotations.command_types import (
    typer_list_arguments,
    typer_list_options,
)
from settings import settings

app = typer.Typer(rich_markup_mode="rich")
_logger = get_logger(__file__)

AppsType = typer_list_options(
    "--apps", "-a", help_msg="Specify an application name on which to run tests."
)
PytestArgsType = typer_list_options(
    "--pytest-args",
    "-p",
    help_msg="List of arguments to pass to the pytest module in string format.",
)
TestPathsType = typer_list_arguments(
    'Test paths to run, run all application tests by default. cannot be combined with the "app" option.',
    of_type=str,
)


@app.command(name="tests", help="Run application tests.")
def run_tests(
    apps: AppsType,
    pytest_args: PytestArgsType,
    test_paths: TestPathsType = None,
):
    """Execute application tests.

    usages:
        > python manage.py tests  # Run all application tests
        > python manage.py tests --apps user authentication  # Run all specific application's tests
        > python manage.py tests /apps/user apps/authentication  # Run all tests of the specified applications
        > python manage.py tests --pytest-args="--ignore=apps/"--pytest-args --strict # Specify pytest args
    """
    dk_compose = DockerComposeRunner(
        settings.BASE_DIR.parent / "docker-compose.test.yaml", env="test"
    )

    test_command = AppTestRunner()

    def _run_test():
        test_command(
            target_apps=apps,
            test_paths=test_paths or [],
            pytest_args=pytest_args,
        )

    dk_compose.run_process(_run_test, stop_after=True, force_recreate=True)
