from core.services.celery import app


@app.task()
def print_message():
    print("This is a periodic task running every 10 seconds.")
