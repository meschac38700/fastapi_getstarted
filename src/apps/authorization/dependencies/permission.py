from typing import Any, Callable, Literal

from fastapi import Request

Fn = Callable[..., Any]


def permission_required_depends(
    permissions: list[str], *, operator: Literal["AND", "OR"] = "AND"
) -> Fn:
    async def dependency(request: Request):
        # TODO(Eliam): Implement permission logics
        print("----------------------------------------")
        print(f"{permissions=}, {operator=}, {request=}")
        print("----------------------------------------")

    return dependency
