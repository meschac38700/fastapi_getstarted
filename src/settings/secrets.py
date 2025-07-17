from pydantic_settings import BaseSettings


class SecretSettings(BaseSettings):
    postgres_password: str = "<PASSWORD>"
    redis_password: str = "<PASSWORD>"

    """
    Application secret key used in different aspects of the application:
        encode JWT token, generate CSRF token etc.
    """
    secret_key: str = ""

    sentry_dsn: str = ""

    # security
    _PASSWORD_HASHERS = [
        "core.auth.hashers.bcrypt.BCryptPasswordHasher",
    ]
    """
    Allows the developer to access one of the password hashes listed in the PASSWORD_HASHERS constant
    """
    password_hasher_index: int = 0
    """
    Used to generate/decode JWT tokens
    """
    algorithm: str = "HS256"

    @property
    def password_hasher(self):
        return self._PASSWORD_HASHERS[self.password_hasher_index]
