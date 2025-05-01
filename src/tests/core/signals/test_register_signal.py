from typing import Callable

import pytest
from sqlalchemy import event as sa_event
from typing_extensions import Any, ParamSpec

from apps.user.models import User
from core.db.signals.managers import signal_manager

P = ParamSpec("P")
Fn = Callable[P, Any]


def foo(*_, **__):
    pass


@pytest.mark.parametrize(
    "target,event_name,callback",
    (
        (User, "before_update", foo),
        (User, "before_insert", foo),
        (User, "after_delete", foo),
    ),
)
def test_register_signal(target: Any, event_name: str, callback: Fn):
    signal_manager.register(event_name, callback, target=target)
    assert sa_event.contains(target, event_name, callback)
    assert len(signal_manager.event_handlers) >= 1


@pytest.mark.parametrize(
    "target,event_name,callback",
    (
        (User, "before_update", foo),
        (User, "before_insert", foo),
        (User, "after_delete", foo),
    ),
)
def test_unregister_signal(target: Any, event_name: str, callback: Fn):
    signal_manager.unregister(event_name, callback, target=target)
    assert sa_event.contains(target, event_name, callback) is False


@pytest.mark.parametrize(
    "target,event_name,callback",
    (
        (User, "on_update", foo),
        (User, "soon_after_delete", foo),
    ),
)
def test_unknown_signal_event_name(target: Any, event_name: str, callback: Fn):
    with pytest.raises(ValueError) as e:
        signal_manager.register(event_name, callback, target=target)
    assert f"Not supported event: {event_name}." in str(e.value)
