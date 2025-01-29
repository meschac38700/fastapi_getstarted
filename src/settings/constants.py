import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# valid env: dev, test, prod
env_name = (os.getenv("APP_ENVIRONMENT") or "prod").lower()
valid_environments = ["prod", "test", "dev"]
if env_name not in valid_environments:
    raise ValueError(
        f"Invalid environment value: {env_name}! Expected: {valid_environments}"
    )

DATABASE_ENV_FILE = BASE_DIR.parent / "envs" / env_name / ".env"

PASSWORD_HASHERS = [
    "core.auth.hashers.bcrypt.BCryptPasswordHasher",
]
PASSWORD_HASHER_INDEX = int(os.getenv("PASSWORD_HASHER_INDEX") or 0)
PASSWORD_HASHER = PASSWORD_HASHERS[PASSWORD_HASHER_INDEX]
ACCESS_TOKEN_EXPIRE_MINUTES = 30

initial_fixtures = [
    "initial-heroes",
]

# Authentication
AUTH_PREFIX_URL = "/auth"
AUTH_URL = f"{AUTH_PREFIX_URL}/token"
