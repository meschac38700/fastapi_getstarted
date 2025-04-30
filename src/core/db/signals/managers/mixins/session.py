from typing import Callable

from sqlmodel import Session
from typing_extensions import Any, ParamSpec

P = ParamSpec("P")
Fn = Callable[P, Any]


class SessionEventMixin:
    """Handle all signals related to a session."""

    # SessionEvents
    def after_bulk_delete(self, session: Session):
        def wrapper(callback: Fn):
            self.register("after_bulk_delete", callback, target=session)

        return wrapper

    def after_bulk_update(self, session: Session):
        def wrapper(callback: Fn):
            self.register("after_bulk_update", callback, target=session)

        return wrapper
