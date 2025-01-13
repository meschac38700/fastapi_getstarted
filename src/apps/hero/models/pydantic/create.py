from ._base import HeroBaseModel


class HeroCreate(HeroBaseModel):
    class ConfigDict:
        orm_mode = False
