from .._base import HeroBase


class HeroBaseModel(HeroBase):
    class Config:
        orm_mode = False
