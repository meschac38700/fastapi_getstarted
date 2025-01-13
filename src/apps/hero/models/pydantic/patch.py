from core.models.utils import optional_fields

from ._base import HeroBaseModel


@optional_fields
class HeroPatch(HeroBaseModel):
    class ConfigDict:
        orm_mode = False
