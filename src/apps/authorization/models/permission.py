from sqlmodel import Field
from typing_extensions import Self

from ._base import PermissionBase


class Permission(PermissionBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)

    @classmethod
    async def generate_crud_permissions(cls: Self, key: str, plural_key: str | None):
        """Create crud permissions for the given key."""
        crud_methods = ["create", "update", "delete"]
        read_key = f"read_{plural_key or key}"

        crud_permissions = [read_key, f"update_{key}"]
        if await Permission.exists(Permission.name in crud_permissions):
            return

        description = "This permission allows user to {0} any {1} instance."
        kwargs_list = [
            {
                "name": read_key,
                "description": description.format("read", key.title),
                "display_name": f"Read {key}",
            }
        ]
        for crud_method in crud_methods:
            kwargs_list.append(
                {
                    "name": f"{crud_method}_{key}",
                    "description": description.format(crud_methods, key.title),
                    "display_name": f"{crud_method.title} {key}",
                }
            )

        return Permission.insert_batch([Permission(**kwargs) for kwargs in kwargs_list])
