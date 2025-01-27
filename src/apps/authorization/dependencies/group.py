from typing import Any, Callable, Literal

from fastapi import Request

Fn = Callable[..., Any]


def group_permission_required_depends(
    permissions: list[str], groups: list[str], *, operator: Literal["AND", "OR"] = "AND"
) -> Fn:
    async def dependency(request: Request):
        # TODO(Eliam): Implement permission logics
        print("----------------------------------------")
        print(f"{permissions=}, {groups=} {operator=}, {request=}")
        print("----------------------------------------")

    return dependency
