import asyncio

from apps.user.models import User
from core.services.celery import celery_app


@celery_app.task()
def create_user_task(**user_data):
    return asyncio.run(User(**user_data).save())
