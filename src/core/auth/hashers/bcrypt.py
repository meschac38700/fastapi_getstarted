from passlib.context import CryptContext


class BCryptPasswordHasher:
    def __init__(self):
        self.ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str):
        return self.ctx.hash(password)

    def verify(self, plain_password: str, hashed_password: str):
        return self.ctx.verify(plain_password, hashed_password)
