import enum


class ContainerState(enum.Enum):
    EXITED = "exited"
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
