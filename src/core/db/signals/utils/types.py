import enum
from typing import Callable

from typing_extensions import Any, NamedTuple, ParamSpec

P = ParamSpec("P")
Fn = Callable[P, Any]


class EventCategory(enum.Enum):
    MAPPER = "mapper"
    SCHEMA = "schema"
    SESSION = "session"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


class EventModel(NamedTuple):
    name: str
    target: Any
    callback: Fn
    category: EventCategory
