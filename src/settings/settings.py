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

DATABASE_ENV_FILE = DB_ENV_FILE = BASE_DIR.parent / "envs" / env_name / ".env"
