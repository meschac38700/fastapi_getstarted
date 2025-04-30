from typing import Callable

from sqlmodel import SQLModel
from typing_extensions import Any, ParamSpec

P = ParamSpec("P")
Fn = Callable[P, Any]


class SchemaEventMixin:
    """Handle all signals related to a user-defined class to a Table object."""

    def before_create(self, model: SQLModel):
        def wrapper(callback: Fn):
            self.register("before_create", callback, target=model)

        return wrapper

    def before_drop(self, model: SQLModel):
        def wrapper(callback: Fn):
            self.register("before_drop", callback, target=model)

        return wrapper

    def after_create(self, model: SQLModel):
        def wrapper(callback: Fn):
            self.register("after_create", callback, target=model)

        return wrapper

    def after_drop(self, model: SQLModel):
        def wrapper(callback: Fn):
            self.register("after_drop", callback, target=model)

        return wrapper
