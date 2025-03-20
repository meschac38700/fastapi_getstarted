# from celery import shared_task
from core.services.celery import celery


@celery.task
def create_user_task(**user_data):
    import asyncio

    from apps.user.models import User

    return asyncio.run(User(**user_data).save())
