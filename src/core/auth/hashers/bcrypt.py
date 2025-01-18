import bcrypt


class BCryptPasswordHasher:
    @classmethod
    def hash(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes = password.encode("utf-8")
        return bcrypt.hashpw(password=pwd_bytes, salt=salt).decode("utf-8")

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        password_byte_enc = plain_password.encode("utf-8")
        return bcrypt.checkpw(password_byte_enc, hashed_password.encode("utf-8"))
