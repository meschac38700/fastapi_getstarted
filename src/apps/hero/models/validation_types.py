from typing import Any

from ._base import HeroBase


class HeroCreate(HeroBase):
    class ConfigDict:
        orm_mode = False


class HeroUpdate(HeroBase):
    age: int

    class ConfigDict:
        orm_mode = False


class HeroPatch(HeroBase):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None

    def check_all_field_updated(self, old_data: dict[str, Any]):
        _old_data = old_data.copy()
        _old_data.pop("id", None)
        current_attrs = self.model_dump(exclude_unset=True).keys()
        all_values_changed = all(
            _old_data[k] != getattr(self, k) for k in current_attrs
        )

        return current_attrs == _old_data.keys() and all_values_changed

    class ConfigDict:
        orm_mode = False
