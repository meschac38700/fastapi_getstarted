from typing import Protocol


class PasswordHasher(Protocol):
    @classmethod
    def hash(cls, password_plain: str) -> str:
        """Define this method in the concrete hash class."""

    @classmethod
    def verify(cls, password_plain: str, hashed_password: str) -> bool:
        """Define this method in the concrete hash class."""
