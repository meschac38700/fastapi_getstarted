from sqlmodel import Field, SQLModel


class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None
