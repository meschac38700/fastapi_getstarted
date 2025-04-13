from core.services.celery import celery_app


@celery_app.task()
def debug_task():
    print("This is a periodic task running every 5 minutes.")
