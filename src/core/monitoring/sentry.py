import sentry_sdk

from settings import settings


def sentry_init():
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=settings.sentry_send_pii,
    )
