from typing import Any

from sqlmodel import SQLModel


class SQLTable(SQLModel):
    @property
    def sql_table_name(self):
        return self.__tablename__

    def update_from_dict(self, data: dict[str, Any]):
        valid_keys = self.model_dump()
        for key, value in data.items():
            if key in valid_keys:
                setattr(self, key, value)
