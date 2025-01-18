from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password_plain: str) -> str:
        pass

    def verify(self, password_plain: str, hashed_password: str) -> bool:
        pass
