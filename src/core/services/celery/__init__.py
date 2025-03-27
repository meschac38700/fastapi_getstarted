from .main import main

celery_app = main()

__all__ = ["celery_app"]
