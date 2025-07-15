class SQLAlchemyIntegrityError(Exception):
    """Custom exception for SQLAlchemy integrity errors.

    This avoids passing the full IntegrityError.
    (which may contain a traceback or a non-serializable DBAPI error)
    """
