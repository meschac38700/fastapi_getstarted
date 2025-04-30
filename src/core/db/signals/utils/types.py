from typing import Callable

from typing_extensions import Any, NamedTuple, ParamSpec

P = ParamSpec("P")
Fn = Callable[P, Any]


class EventModel(NamedTuple):
    name: str
    target: Any
    callback: Fn
