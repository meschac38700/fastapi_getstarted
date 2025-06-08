from core.db.utils import optional_fields

from ._base import HeroBaseModel


@optional_fields
class HeroPatch(HeroBaseModel):
    class ConfigDict:
        from_attributes = True
