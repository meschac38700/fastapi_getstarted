from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class YAMLReader:
    file_path: str | Path

    def __post_init__(self):
        if not self.file_path.exists() or not self.file_path.is_file():
            raise ValueError(
                f"You have to specify an existing valid file: ${self.file_path}"
            )

    def read(self):
        return yaml.safe_load(self.file_path.read_text())
