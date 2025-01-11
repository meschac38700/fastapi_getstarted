from typing import Any

from sqlmodel import SQLModel

from core.db.query import ModelQuery


class SQLTable(SQLModel, ModelQuery):
    @classmethod
    def table_name(cls):
        return cls.__tablename__

    def update_from_dict(self, data: dict[str, Any]):
        valid_keys = self.model_dump()
        for key, value in data.items():
            if key in valid_keys:
                setattr(self, key, value)
