from functools import wraps
from typing import Any, Callable, Literal

Fn = Callable[..., Any]


def permission_required(
    permissions: list[str], *, operator: Literal["AND", "OR"] = "AND"
):
    def decorator(func) -> Fn:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TODO(Eliam): Implement permission logics
            print("----------------------------------------")
            print(f"{permissions=}, {operator=}, {kwargs.get("request")=}")
            print("----------------------------------------")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
