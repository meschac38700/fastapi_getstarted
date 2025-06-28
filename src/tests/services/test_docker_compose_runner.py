from pathlib import Path
from unittest import TestCase, mock

from core.services.docker.compose import DockerComposeRunner
from core.services.docker.mock import MockDockerRunner
from core.services.docker.types import ContainerState


class TestDockerManager(TestCase):
    def setUp(self):
        self.docker_compose_file = (
            Path(__file__).parent / "data" / "test.docker-compose.yaml"
        )

    def test_init_docker_compose_manager_successfully(self):
        docker_runner = DockerComposeRunner(self.docker_compose_file, env="test")
        self.assertEqual(1, len(docker_runner.get_compose_services()))
        self.assertEqual(("web",), docker_runner.get_compose_services())
        self.assertEqual(("web",), docker_runner.required_services)

    @mock.patch(__name__ + ".DockerComposeRunner", side_effect=MockDockerRunner)
    def test_up_and_down_docker_compose_services(
        self, mock_runner_class: type(MockDockerRunner)
    ):
        docker_runner = DockerComposeRunner(self.docker_compose_file, env="test")
        self.assertIsInstance(docker_runner, MockDockerRunner)
        self.assertIs(DockerComposeRunner, mock_runner_class)
        self.assertEqual(["web"], docker_runner.get_not_running_services())

        docker_runner.start_services()

        self.assertEqual([], docker_runner.get_not_running_services())
        self.assertEqual(
            ["web"], docker_runner.get_services_by_state(ContainerState.RUNNING)
        )

        docker_runner.stop_services()
        self.assertEqual(["web"], docker_runner.get_not_running_services())
        self.assertEqual(
            [], docker_runner.get_services_by_state(ContainerState.RUNNING)
        )
        self.assertEqual(
            ["web"], docker_runner.get_services_by_state(ContainerState.STOPPED)
        )

    def test_invalid_docker_compose_file_type(self):
        with self.assertRaises(ValueError) as e:
            DockerComposeRunner(f"{str(self.docker_compose_file)}".encode(), env="test")
        self.assertIn(
            "docker_compose file must be a string or a Path", str(e.exception)
        )

    def test_docker_compose_override_files(self):
        override_file = (
            Path(__file__).parent / "data" / "override.test.docker-compose.yaml"
        )
        docker_runner = DockerComposeRunner(
            self.docker_compose_file,
            env="test",
            override_compose_files=[override_file],
            required_services=("php",),
        )

        self.assertEqual(docker_runner.get_compose_services(), ("web", "php"))

    def test_docker_compose_file_not_exists(self):
        dc_file = self.docker_compose_file / "aze.yaml"
        override_file = (
            Path(__file__).parent / "data" / "override.test.docker-compose.yaml"
        )
        with self.assertRaises(FileNotFoundError) as e:
            docker_runner = DockerComposeRunner(
                dc_file, env="test", override_compose_files=[override_file]
            )
            docker_runner.start_services()
        self.assertIn(
            f"Docker compose file does not exist: '{dc_file}'.", str(e.exception)
        )

    @mock.patch(__name__ + ".DockerComposeRunner", side_effect=MockDockerRunner)
    def test_run_process(self, _):
        override_file = (
            Path(__file__).parent / "data" / "override.test.docker-compose.yaml"
        )
        docker_runner = DockerComposeRunner(
            self.docker_compose_file, env="test", override_compose_files=[override_file]
        )

        def _callback():
            nonlocal docker_runner
            assert docker_runner.get_services_by_state(ContainerState.RUNNING) == [
                "web",
                "php",
            ]

        self.assertEqual(["web", "php"], docker_runner.get_not_running_services())
        docker_runner.run_process(_callback)

        self.assertEqual(
            ["web", "php"], docker_runner.get_services_by_state(ContainerState.STOPPED)
        )
