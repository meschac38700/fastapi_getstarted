from .collect_statics import app as collect_statics_command
from .fixtures import app as fixture_command
from .health_check import app as health_check_command
from .run_tests import app as test_command
from .server import app as server_command

__all__ = [
    "test_command",
    "server_command",
    "fixture_command",
    "health_check_command",
    "collect_statics_command",
]
