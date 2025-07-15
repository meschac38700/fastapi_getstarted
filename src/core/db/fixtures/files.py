import itertools
from dataclasses import dataclass

from core.db.fixtures.utils import ModelDataType
from core.services.files import YAMLReader


@dataclass
class FixtureFileReader(YAMLReader):
    async def extract_data(self) -> dict[str, list[ModelDataType]]:
        """Extract data from fixture file and group them by app.model."""
        data_list = await self.read_async()
        return {
            grp_key: list(grp)
            for grp_key, grp in itertools.groupby(data_list, key=lambda m: m["model"])
        }
