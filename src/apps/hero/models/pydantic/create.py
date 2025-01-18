from ._base import HeroBaseModel


class HeroCreate(HeroBaseModel):
    class ConfigDict:
        from_attributes = True
