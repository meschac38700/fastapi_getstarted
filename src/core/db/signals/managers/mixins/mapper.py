from typing import Callable

from sqlmodel import SQLModel
from typing_extensions import Any, ParamSpec

from core.db.signals.utils.types import EventCategory

P = ParamSpec("P")
Fn = Callable[P, Any]


class MapperEventMixin:
    """Handle all signals related to a user-defined class to a Table object.

    Docs: https://docs.sqlalchemy.org/en/20/orm/events.html#mapper-events
    """

    def before_delete(self, model: SQLModel):
        def wrapper(fn: Fn):
            return self.register(
                "before_delete", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper

    def before_update(self, model: SQLModel):
        def wrapper(fn: Fn):
            self.register(
                "before_update", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper

    def before_insert(self, model: SQLModel):
        def wrapper(fn: Fn):
            self.register(
                "before_insert", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper

    def after_delete(self, model: SQLModel):
        def wrapper(fn: Fn):
            self.register(
                "after_delete", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper

    def after_update(self, model: SQLModel):
        def wrapper(fn: Fn):
            self.register(
                "after_update", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper

    def after_insert(self, model: SQLModel):
        def wrapper(fn: Fn):
            self.register(
                "after_insert", fn, target=model, category=EventCategory.MAPPER
            )

        return wrapper
