import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# valid env: dev, test, prod
env = (os.getenv("APP_ENVIRONMENT") or "prod").lower()
valid_environments = ["prod", "test", "dev"]
if env not in valid_environments:
    raise ValueError(
        f"Invalid environment value: {env}! Expected: {valid_environments}"
    )

DATABASE_ENV_FILE = DB_ENV_FILE = BASE_DIR.parent / "envs" / env / ".env"
