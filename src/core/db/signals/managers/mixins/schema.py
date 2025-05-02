from typing import Callable

from sqlmodel import SQLModel
from typing_extensions import Any, ParamSpec

from core.db.signals.utils.types import EventCategory

P = ParamSpec("P")
Fn = Callable[P, Any]


class SchemaEventMixin:
    """Define event listeners for schema objects, that is, SchemaItem and other
    SchemaEventTarget subclasses, including MetaData, Table, Column, etc.

    Docs: https://docs.sqlalchemy.org/en/20/core/events.html#schema-events
    """

    def before_create(self, model: SQLModel):
        """Handle event before CREATE sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "before_create", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def before_drop(self, model: SQLModel):
        """Handle event before DROP sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "before_drop", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def after_create(self, model: SQLModel):
        """Handle event after CREATE sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "after_create", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper

    def after_drop(self, model: SQLModel):
        """Handle event after DROP sql command is emitted to the database."""

        def wrapper(callback: Fn):
            self.register(
                "after_drop", callback, target=model, category=EventCategory.SCHEMA
            )

        return wrapper
