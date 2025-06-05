from .._base import HeroBase


class HeroBaseModel(HeroBase):
    class ConfigDict:
        from_attributes = True
