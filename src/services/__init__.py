from .db import get_db_service

db_service = get_db_service()

__all__ = ["db_service"]
