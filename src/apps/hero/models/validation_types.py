from ._base import HeroBase


class HeroCreate(HeroBase):
    class ConfigDict:
        orm_mode = False
