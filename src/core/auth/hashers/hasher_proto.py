from typing import Protocol


class PasswordHasher(Protocol):
    @classmethod
    def hash(cls, password_plain: str) -> str:
        pass

    @classmethod
    def verify(cls, password_plain: str, hashed_password: str) -> bool:
        pass
