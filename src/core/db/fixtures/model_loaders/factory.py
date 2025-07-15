from core.db.fixtures.model_loaders.default import DefaultLoader
from core.db.fixtures.model_loaders.user import UserLoader
from core.db.fixtures.utils import ModelDataType


class ModelLoaderFactory:
    def __init__(self):
        self._loaders = {
            "user.User": UserLoader,
        }

    def get_loader(self, loader_type: str):
        return self._loaders.get(loader_type, DefaultLoader)

    async def load(self, model_data: list[ModelDataType], loader_type: str):
        loader = self.get_loader(loader_type)
        return await loader().load(model_data)
