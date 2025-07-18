from ._base import AppBaseSettings


class SecretSettings(AppBaseSettings):
    postgres_password: str = "<PASSWORD>"
    redis_password: str = "<PASSWORD>"

    sentry_dsn: str = ""

    # security
    _PASSWORD_HASHERS = [
        "core.auth.hashers.bcrypt.BCryptPasswordHasher",
    ]
    """
    Choose one of the listed password hashes in the PASSWORD_HASHERS settings. default take the first one.
    """
    password_hasher_index: int = 0
    """
    Used to generate/decode JWT tokens
    """
    algorithm: str = "HS256"

    @property
    def password_hasher(self):
        return self._PASSWORD_HASHERS[self.password_hasher_index]
