from typing import Any

from ._base import HeroBase


class HeroCreate(HeroBase):
    class ConfigDict:
        orm_mode = False


class HeroUpdate(HeroBase):
    age: int

    class ConfigDict:
        orm_mode = False

    def check_all_field_updated(self, old_data: dict[str, Any]):
        current_attrs = self.model_dump().keys()
        all_values_changed = all(old_data[k] != getattr(self, k) for k in current_attrs)
        return current_attrs == old_data.keys() and all_values_changed
