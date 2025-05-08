from typing import Callable

from sqlalchemy import Table
from typing_extensions import Any, ParamSpec

from core.db.signals.utils.types import EventCategory

P = ParamSpec("P")
Fn = Callable[P, Any]


class SchemaEventMixin:
    """Define event listeners for schema objects, that is, SchemaItem and other
    SchemaEventTarget subclasses, including MetaData, Table, Column, etc.

    Docs: https://docs.sqlalchemy.org/en/20/core/events.html#schema-events

    Example:
    >>> from sqlalchemy import Connection, Table
    >>>
    >>> from core.db.signals.managers import signal_manager
    >>> from apps.user.models import User
    >>>
    >>>
    >>> @signal_manager.before_create(User.table())
    >>> def before_create_user_table(target: Table, connection: Connection, **kwargs):
    >>>     pass
    >>>
    """

    def before_create(self, model: Table):
        """Handle event before CREATE sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "before_create", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def before_drop(self, model: Table):
        """Handle event before DROP sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "before_drop", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def after_create(self, model: Table):
        """Handle event after CREATE sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "after_create", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def after_drop(self, model: Table):
        """Handle event after DROP sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "after_drop", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper
