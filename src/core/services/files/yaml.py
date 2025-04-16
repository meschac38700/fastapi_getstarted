import logging
from dataclasses import dataclass
from pathlib import Path

import aiofiles
import yaml

from core.monitoring.logger import get_logger

_logger = get_logger(__name__)


@dataclass
class YAMLReader:
    file_path: str | Path
    logger: logging.Logger | None = None

    def __post_init__(self):
        self.logger = self.logger or _logger

        if not self.file_path.exists() or not self.file_path.is_file():
            raise ValueError(f"File does not exist: ${self.file_path}")

    def read(self):
        return yaml.safe_load(self.file_path.read_text())

    async def read_async(self):
        async with aiofiles.open(self.file_path, mode="r") as f:
            return yaml.safe_load(await f.read())
