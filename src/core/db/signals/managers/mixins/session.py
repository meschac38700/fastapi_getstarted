from typing import Callable

from sqlmodel import Session
from typing_extensions import Any, ParamSpec

P = ParamSpec("P")
Fn = Callable[P, Any]


class SessionEventMixin:
    """Handle all signals at the level of the ORM Session.

    Docs: https://docs.sqlalchemy.org/en/20/orm/events.html#session-events
    """

    # SessionEvents
    def after_bulk_delete(self, session: Session):
        """Event for after the legacy Query.delete() method has been called.

        Docs: https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.SessionEvents.after_bulk_delete
        """

        def wrapper(callback: Fn):
            self.register("after_bulk_delete", callback, target=session)

        return wrapper

    def after_bulk_update(self, session: Session):
        """Event for after the legacy Query.update() method has been called.

        Docs: https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.SessionEvents.after_bulk_update
        """

        def wrapper(callback: Fn):
            self.register("after_bulk_update", callback, target=session)

        return wrapper
