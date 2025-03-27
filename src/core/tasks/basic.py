from core.services.celery import celery_app


@celery_app.task()
def print_message():
    print("This is a periodic task running every 10 seconds.")
