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
