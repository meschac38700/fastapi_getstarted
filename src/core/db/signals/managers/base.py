import typing
from functools import lru_cache
from typing import Any, Callable, Literal, ParamSpec, TypeAlias

from sqlalchemy import event as sa_event

from core.db.signals.managers.mixins import (
    MapperEventMixin,
    SchemaEventMixin,
    SessionEventMixin,
)
from core.db.signals.utils.types import EventCategory, EventModel
from core.monitoring.logger import get_logger

P = ParamSpec("P")
Fn = Callable[P, Any]
EventName: TypeAlias = Literal[
    # mapper events
    "after_delete",
    "after_insert",
    "after_update",
    "before_delete",
    "before_insert",
    "before_update",
    # schema events
    "before_create",
    "before_drop",
    "after_create",
    "after_drop",
    # session events
    "after_bulk_delete",
    "after_bulk_update",
]
logger = get_logger(__name__)


class SignalManager(MapperEventMixin, SchemaEventMixin, SessionEventMixin):
    EVENT_NAMES = typing.get_args(EventName)

    def __init__(self):
        self.event_handlers: list[EventModel] = []
        self.logger = logger

    def _guard_unknown_event_name(self, event_name: EventName):
        """Raise an error if the given event name is unknown."""
        if event_name not in self.EVENT_NAMES:
            raise ValueError(f"Not supported event: {event_name}.")

    def register(
        self,
        event_name: EventName,
        callback: Fn,
        *,
        target: Any,
        category: EventCategory,
    ):
        self._guard_unknown_event_name(event_name)

        event = EventModel(
            name=event_name, target=target, callback=callback, category=category
        )
        self.logger.info(f"Signal registering {event}")
        if sa_event.contains(target, event_name, callback):
            return

        self.event_handlers.append(event)
        sa_event.listens_for(target, event_name)(callback)

    def unregister(
        self,
        event_name: EventName,
        callback: Fn,
        *,
        target: Any,
        category: EventCategory,
    ):
        self._guard_unknown_event_name(event_name)

        event = EventModel(
            name=event_name, target=target, callback=callback, category=category
        )
        self.logger.info(f"Signal unregistering {event}")
        if not sa_event.contains(target, event_name, callback):
            return

        sa_event.remove(target, event_name, callback)
        self.event_handlers.remove(event)


@lru_cache
def get_signal_manager():
    return SignalManager()
