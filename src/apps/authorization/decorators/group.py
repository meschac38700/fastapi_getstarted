from functools import wraps
from typing import Any, Callable, Literal

from fastapi import Request

Fn = Callable[..., Any]


def group_permission_required(
    permissions: list[str], groups: list[str], operator: Literal["AND", "OR"] = "AND"
):
    def decorator(func: Fn) -> Fn:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            # TODO(Eliam): implement group permission logics
            return func(*args, **kwargs)

        return wrapper

    return decorator
