import os
from typing import Literal


class AppConstants:
    APP_ENVIRONMENT: Literal["prod", "test", "dev"] = os.getenv("APP_ENVIRONMENT")
    APP_PORT: int

    INITIAL_FIXTURES = [
        "initial-users",
        "initial-heroes",
    ]

    # Authentication
    AUTH_PREFIX_URL = "/auth"
    API_ROUTER_PREFIX = "/api"
    WEB_ROUTER_PREFIX = "/web"
    AUTH_URL = f"{API_ROUTER_PREFIX}{AUTH_PREFIX_URL}/token/"
    SESSION_AUTH_URL = f"{WEB_ROUTER_PREFIX}{AUTH_PREFIX_URL}/session/"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    """
        Maximum time, in minutes, after the token expires during which it can still be refreshed,
        otherwise the user must reauthenticate
    """
    TOKEN_REFRESH_DELAY_MINUTES = 30

    """
        All URL paths that begin with the paths listed
        below are exempt from authentication.
    """
    EXEMPT_AUTH_URLS = {
        AUTH_PREFIX_URL,
        ".*/auth.*",
        "/docs/?.*",
        "/static/.*",
        ".*/?openapi.json.*",
        "/redoc",
        "/default/?.*",
    }

    # Templating
    TEMPLATE_DIR = "templates"
    STATIC_URL = "/static/"
    """
        This folder is located at the root of the project,
        at the same level as the src folder. By default, the name is "statics".
        If you decide to change it, you must also rename the folder at the root, and finally,
        in each application (apps/my_application/), you should also name the static folder with the same name.
        example:
            apps/user/{static_folder_name}
            apps/authentication/{static_folder_name}
    """
    STATIC_ROOT = "statics"

    TEST_BASE_URL = "https://test.code"

    # prometheus client
    METRICS_PATH = "/metrics"
