from unittest.async_case import IsolatedAsyncioTestCase

import pytest

from settings import settings


@pytest.mark.celery(
    result_backend=settings.celery_backend, broker=settings.celery_broker
)
class TestCeleryCase(IsolatedAsyncioTestCase):
    pass
