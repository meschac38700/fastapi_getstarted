import datetime

import settings

_TOKEN_REFRESH_SAFETY_MINUTES = 5


def token_expire_datetime(created_at: datetime.datetime | None = None):
    start_dt = created_at or datetime.datetime.now(datetime.timezone.utc)
    dt = start_dt + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return dt.replace(tzinfo=datetime.timezone.utc)
