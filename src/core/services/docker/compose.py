import logging
import re
import subprocess
import time
from collections.abc import Callable
from logging import Logger
from pathlib import Path
from typing import Any, Literal

import yaml

import settings

Fn = Callable[..., Any]
logger = logging.getLogger(__name__)


class DockerComposeManager:
    """Manager to run docker compose services."""

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
        self.required_services = required_services or self._get_compose_services()
        self.logger = p_logger or logger

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
            ValueError: if the provided path not exists or None.
        """
        if not isinstance(docker_compose_file, str) and not isinstance(
            docker_compose_file, Path
        ):
            raise ValueError("docker_compose file must be a string or a Path")

        self.docker_compose_file = settings.BASE_DIR.parent / Path(docker_compose_file)

        self.override_compose_files = []
        for compose_file in override_files:
            self.override_compose_files.append(
                settings.BASE_DIR.parent / Path(compose_file)
            )

    def _get_compose_services(self) -> tuple[str, ...]:
        """Return all the service names from the provided docker compose
        file."""
        with open(self.docker_compose_file) as f:
            docker_data: dict[str, Any] = yaml.safe_load(f)
        return tuple({name for name, _ in docker_data["services"].items()})

    def _get_not_running_services(self, states: str) -> list[str] | tuple[str, ...]:
        """Return list of services that have not been started yet.

        @params state: The state of the all the current services. Can be 'running', 'stopped'
            available format: "exited"  "created" "running" "created"
        """
        if not states and self.required_services:
            return self.required_services

        state_list = re.findall(r"\w+", states)  # extract all services status
        return [
            service
            for state, service in zip(state_list, self.required_services)
            if state.lower() != "running"
        ]

    def _has_pending_services(self) -> list[str]:
        """Check if the provided 'required_services' or all the docker compose
        services are up."""
        if not self.required_services:
            return []

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
        # return list of services that are not running
        return self._get_not_running_services(container_state)

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

        if any error force down the services already up.
        """
        self.logger.info("Setting environment...")

        if not self.docker_compose_file.exists():
            raise FileNotFoundError(
                f"Docker compose file does not exist: '{self.docker_compose_file}'."
            )

        self._run_docker_compose_services(force_recreate)

    def stop_services(self) -> None:
        """Stop all the services related to the dockerfile."""
        self.logger.info("Shutting down environment.")
        output: subprocess.CompletedProcess[bytes] = subprocess.run(
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
        if self.docker_compose_file.exists() and output:
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
        while pending_svc := self._has_pending_services():
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
        self._wait_for_services()
        self._apply_callback(callback, stop_after)
