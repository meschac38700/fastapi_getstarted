import os
from typing import Literal


class AppConstants:
    APP_ENVIRONMENT: Literal["prod", "test", "dev"] = os.getenv("APP_ENVIRONMENT")

    INITIAL_FIXTURES = [
        "initial-users",
        "initial-heroes",
    ]

    # Authentication
    AUTH_PREFIX_URL = "/auth"
    AUTH_URL = f"{AUTH_PREFIX_URL}/token"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    """
        Maximum time, in minutes, after the token expires during which it can still be refreshed,
        otherwise the user must reauthenticate
    """
    TOKEN_REFRESH_DELAY_MINUTES = 30

    # Templating
    TEMPLATE_DIR = "templates"
