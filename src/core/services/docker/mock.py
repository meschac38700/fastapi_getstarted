from core.services.docker.compose import ContainerState, DockerComposeRunner


class MockDockerRunner(DockerComposeRunner):
    """Simple mock class for DockerComposeRunner."""

    desired_state: ContainerState = ContainerState.EXITED

    @property
    def _get_required_container_states(self) -> list[ContainerState]:
        return [self.desired_state.value for _ in self.required_services]

    def _run_docker_compose_services(self, _: bool = False):
        self.desired_state = ContainerState.RUNNING

    def stop_services(self) -> None:
        self.desired_state = ContainerState.STOPPED
