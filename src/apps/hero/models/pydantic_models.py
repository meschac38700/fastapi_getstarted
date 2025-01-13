from core.models.utils import optional_fields

from ._base import HeroBase


class HeroCreate(HeroBase):
    class ConfigDict:
        orm_mode = False


@optional_fields
class HeroPatch(HeroBase):
    class ConfigDict:
        orm_mode = False
