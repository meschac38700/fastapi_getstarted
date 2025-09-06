import functools
from unittest.mock import patch

from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class Popen:
    return_code: int = 0

    def __call__(self, *args, **kwargs):
        logger.info("Process executed successfully.")
        return self

    def wait(self):
        return self.return_code

    @property
    def returncode(self):
        return self.return_code


class Subprocess:
    PIPE = -1
    STDOUT = -2
    DEVNULL = -3
    Popen = Popen()


def mock_popen(subprocess_path: str, *, error: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if error:
                Subprocess.Popen.return_code = 1

            with patch(subprocess_path, Subprocess) as _:
                return func(*args, **kwargs)

        return wrapper

    return decorator
