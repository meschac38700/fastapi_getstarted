import logging
import os
import subprocess

from core.monitoring.logger import get_logger

_logger = get_logger(__name__)


class ServerRunner:
    def __init__(
        self,
        *,
        port: int = 8000,
        host: str = "127.0.0.1",
        reload: bool = True,
        p_logger: logging.Logger | None = None,
    ):
        self.host = host
        self.port = port
        self.reload = reload
        self.logger = p_logger or _logger

    def _start_server(self):
        """Run fastapi development server."""
        self.logger.info("Start dev server...")

        _env = {"HOST": self.host, "PORT": str(self.port), "RELOAD": str(self.reload)}
        ps = subprocess.Popen(
            ["sh", "src/scripts/local_server.sh"],
            stdin=subprocess.PIPE,
            env=dict(os.environ, **_env),
        )
        return ps.wait()

    def __call__(self):
        self._start_server()
