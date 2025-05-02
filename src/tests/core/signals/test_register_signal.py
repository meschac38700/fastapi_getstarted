from typing import Callable

import pytest
from sqlalchemy import event as sa_event
from typing_extensions import Any, ParamSpec

from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.db.signals.utils.types import EventCategory

P = ParamSpec("P")
Fn = Callable[P, Any]


def foo(*_, **__):
    pass


@pytest.mark.parametrize(
    "target,event_name,callback,category",
    (
        (User, "before_update", foo, EventCategory.MAPPER),
        (User, "before_insert", foo, EventCategory.MAPPER),
        (User, "after_delete", foo, EventCategory.MAPPER),
    ),
)
def test_register_signal(
    target: Any, event_name: str, callback: Fn, category: EventCategory
):
    signal_manager.register(event_name, callback, target=target, category=category)
    assert sa_event.contains(target, event_name, callback)
    assert len(signal_manager.event_handlers) >= 1


@pytest.mark.parametrize(
    "target,event_name,callback,category",
    (
        (User, "before_update", foo, EventCategory.MAPPER),
        (User, "before_insert", foo, EventCategory.MAPPER),
        (User, "after_delete", foo, EventCategory.MAPPER),
    ),
)
def test_unregister_signal(
    target: Any, event_name: str, callback: Fn, category: EventCategory
):
    signal_manager.unregister(event_name, callback, target=target, category=category)
    assert sa_event.contains(target, event_name, callback) is False


@pytest.mark.parametrize(
    "target,event_name,callback,category",
    (
        (User, "on_update", foo, EventCategory.MAPPER),
        (User, "soon_after_delete", foo, EventCategory.MAPPER),
    ),
)
def test_unknown_signal_event_name(
    target: Any, event_name: str, callback: Fn, category: EventCategory
):
    with pytest.raises(ValueError) as e:
        signal_manager.register(event_name, callback, target=target, category=category)
    assert f"Not supported event: {event_name}." in str(e.value)
