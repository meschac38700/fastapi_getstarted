from core.db import SQLTable
from core.db.fixtures.model_loaders.base import ModelBaseLoader
from core.db.fixtures.utils import ModelDataType


class DefaultLoader(ModelBaseLoader[SQLTable]):
    async def load(self, data_list: list[ModelDataType]):
        await SQLTable.bulk_create_or_update(self._to_instances(data_list))
