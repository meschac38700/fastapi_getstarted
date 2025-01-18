from collections.abc import Iterator
from typing import Any

from sqlmodel import SQLModel

from core.db.query import ModelQuery

_EMPTY = type("Empty", (), {})


class SQLTable(SQLModel, ModelQuery):
    _updated: bool = False

    @classmethod
    def table_name(cls):
        return cls.__tablename__

    def update_from_dict(self, data: dict[str, Any]):
        for key, value in data.items():
            self_val = getattr(self, key, _EMPTY)
            if self_val is not _EMPTY:
                setattr(self, key, value)

    @property
    def is_updated(self) -> bool:
        return self._updated

    @property
    def required_fields(self) -> Iterator[str]:
        for name, field in self.model_fields.items():
            if not field.is_required():
                continue
            yield name

    def check_all_fields_updated(
        self, old_data: dict[str, Any], *, required: bool = False
    ):
        _old_data = old_data.copy()
        _old_data.pop("id", None)
        current_attrs = self.model_dump(exclude_unset=True).keys()

        all_field_filled = len(_old_data.keys()) == len(current_attrs)
        if required:
            required_fields = list(self.required_fields)
            all_field_filled = all(k in current_attrs for k in required_fields)
            current_attrs = list(required_fields)

        self._updated = any(_old_data[k] != getattr(self, k) for k in current_attrs)
        return all_field_filled

    def check_all_required_fields_updated(
        self,
        old_data: dict[str, Any],
    ):
        """Check all required fields are updated."""
        return self.check_all_fields_updated(old_data, required=True)
