import re
import subprocess
import time
from collections.abc import Callable
from contextlib import ExitStack
from logging import Logger
from pathlib import Path
from typing import Any, Literal

import yaml

from core.monitoring.logger import get_logger
from core.services.docker.types import ContainerState
from settings import settings

Fn = Callable[..., Any]
logger = get_logger(__name__)


class DockerComposeRunner:
    """Runner for a Docker compose YAML file.

    You can provide a callback that will be executed once all services are up and running.
    """

    docker_compose_file: Path | str
    override_compose_files: list[Path]

    def __init__(
        self,
        compose_file: str | Path,
        *,
        override_compose_files: list[str] | list[Path] | None = None,
        env: Literal["test", "prod", "dev"] = "dev",
        required_services: tuple[str, ...] | None = None,
        p_logger: Logger | None = None,
    ):
        """Init docker service.

        Args:
            compose_file (str | Path): docker compose file to start.
            required_services (str | None, optional): the image names used as a witness to
                wait for startup before running dependent processes.
                All provided image names must have a running container. Defaults to None.
            p_logger (Logger | None, optional): logger. Defaults to None.
        """
        self._set_dockerfiles(compose_file, override_compose_files or [])
        self.env = env
        self._required_services = required_services
        self.logger = p_logger or logger

    @property
    def required_services(self) -> tuple[str, ...]:
        return self._required_services or self.get_compose_services()

    def _set_dockerfiles(
        self,
        docker_compose_file: str | Path,
        override_files: list[str] | list[Path] | None = None,
    ) -> None:
        """Set docker_compose_file from the given file if exists.

        Args:
            docker_compose_file (str | Path | None, optional): User's docker compose file. Defaults to None.
            override_files (list[str] | list[Path] | None, optional): User's docker compose file. Defaults to None.

        Raises:
            ValueError: if the provided path does not exist or None.
        """
        if not isinstance(docker_compose_file, str) and not isinstance(
            docker_compose_file, Path
        ):
            raise ValueError("docker_compose file must be a string or a Path")

        self.docker_compose_file = Path(docker_compose_file).absolute()

        self.override_compose_files = []
        for compose_file in override_files:
            self.override_compose_files.append(
                settings.BASE_DIR.parent / Path(compose_file)
            )

    def get_compose_services(self) -> tuple[str, ...]:
        """Return all the service names from the provided docker compose
        file."""
        services = []
        with open(self.docker_compose_file) as f:
            docker_data: dict[str, Any] = yaml.safe_load(f)
            services = [name for name, _ in docker_data["services"].items()]

        with ExitStack() as stack:
            for file_name in self.override_compose_files:
                _file = stack.enter_context(open(file_name))
                docker_data: dict[str, Any] = yaml.safe_load(_file)
                services.extend([name for name, _ in docker_data["services"].items()])

        return tuple(services)

    def get_not_running_services(self) -> list[str]:
        """Return required services that are not running."""
        if not self.required_services:
            return []

        # return list of services that are not running
        return self.get_services_by_state(ContainerState.RUNNING, equals=False)

    def get_services_by_state(
        self, p_state: ContainerState, *, equals: bool = True
    ) -> list[str]:
        """Filter required services by the given state.

        @params state: The desired state of the services.
        @params not_equals: If true, return services that do not match the given states.
        """
        services = []
        current_states = self._get_required_container_states
        if not current_states:
            return list(self.required_services)

        for state, service in zip(current_states, self.required_services):
            if equals and state.lower() == p_state.value:
                services.append(service)
                continue

            if not equals and state.lower() != p_state.value:
                services.append(service)

        return services

    @property
    def _get_required_container_states(self) -> list[ContainerState]:
        container_state = (
            subprocess.run(
                [
                    "docker",
                    "inspect",
                    "-f",
                    "'{{json .State.Status }}'",
                    *self.required_services,
                ],
                capture_output=True,
                check=False,
            )
            .stdout.decode("utf-8")
            .replace("\n", "")
        )
        return re.findall(r"\w+", container_state)  # extract all services status

    def _run_docker_compose_services(self, force_recreate: bool = False):
        """Try to run services of the provided docker compose file."""
        try:
            cmd = [
                "docker",
                "compose",
                "-f",
                self.docker_compose_file,
                *sum(
                    [
                        ["-f", override_file]
                        for override_file in self.override_compose_files
                    ],
                    [],
                ),
                "up",
                "--quiet-pull",
                "--no-log-prefix",
                "-d",
                "--wait",
                "--wait-timeout",
                "10",
            ]

            if force_recreate:
                cmd.extend(["--force-recreate"])

            out = subprocess.Popen(cmd)
            time.sleep(2)
            self.logger.info(f"All docker services successfully up: {out}")
            return out.wait()
        except subprocess.CalledProcessError as e:
            self.logger.debug(f"Error while setting up environment: {e}")
            return self.stop_services()

    def start_services(self, force_recreate: bool = False) -> None:
        """Start docker services.

        if any error forces down, the services already up.
        """
        self.logger.info("Setting environment...")

        if not self.docker_compose_file.exists():
            raise FileNotFoundError(
                f"Docker compose file does not exist: '{self.docker_compose_file}'."
            )

        self._run_docker_compose_services(force_recreate)
        self._wait_for_services()

    def stop_services(self) -> None:
        """Stop all the services related to the dockerfile."""
        self.logger.info("Shutting down environment.")
        container_ids: subprocess.CompletedProcess[bytes] = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(self.docker_compose_file),
                "ps",
                "-q",
            ],
            capture_output=True,
            check=False,
        )
        if self.docker_compose_file.exists() and container_ids:
            args = [
                "docker",
                "compose",
                "-f",
                self.docker_compose_file,
                "down",
            ]
            if self.env == "test":
                args.extend(["--volumes"])

            subprocess.run(args, check=False)

    def _wait_for_services(self):
        """Wait for all services to up."""
        while pending_svc := self.get_not_running_services():
            self.logger.info(f'Waiting for services "{pending_svc}"" to be up...')
            time.sleep(2)

    def _apply_callback(self, callback: Fn, stop_after: bool = False) -> None:
        try:
            callback()
        except KeyboardInterrupt:
            self.logger.info("Program interrupted. stop docker services...")
        finally:
            if stop_after:
                self.stop_services()

    def run_process(
        self,
        callback: Fn,
        *,
        stop_after: bool = True,
        force_recreate: bool = False,
    ) -> None:
        """Start docker services, apply the provided callback and stop services
        if stop_after is True."""
        self.start_services(force_recreate=force_recreate)
        self._apply_callback(callback, stop_after)
