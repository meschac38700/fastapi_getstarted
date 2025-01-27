from typing import Any

from sqlmodel import Field

from ._base import PermissionBase


class Permission(PermissionBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)

    @classmethod
    def _crud_permissions_sql(cls, data_list: list[dict[str, Any]]) -> str:
        sql = ""
        for i, data in enumerate(data_list):
            cols = f'{", ".join(data.keys())}'
            vals = tuple(data.values())
            if i > 0:
                sql += f""",\n {vals}"""
                continue

            sql += f"""INSERT INTO {cls.table_name()}({cols}) VALUES{vals}"""
        return sql + ";"

    @classmethod
    def get_model_crud_permissions(
        cls, table: str, *, plural_table: str | None = None, raw_sql: bool = False
    ) -> list[dict[str, Any]] | str:
        crud_methods = ["create", "update", "delete"]

        description = "This permission allows user to {0} any {1} instance."
        kwargs_list = [
            {
                "name": f"read_{plural_table or table}",
                "description": description.format("read", table.title()),
                "display_name": f"Read {table}",
                "target_table": table,
            }
        ]
        for crud_method in crud_methods:
            kwargs_list.append(
                {
                    "name": f"{crud_method}_{table}",
                    "description": description.format(crud_method, table.title()),
                    "display_name": f"{crud_method.title()} {table}",
                    "target_table": table,
                }
            )
        if raw_sql:
            return cls._crud_permissions_sql(kwargs_list)

        return kwargs_list

    @classmethod
    async def generate_crud_permissions(
        cls, table: str, plural_table: str | None = None
    ):
        """Create crud permissions for the given table."""
        crud_permissions = [f"read_{plural_table or table}", f"update_{table}"]
        if await Permission.get(Permission.name in crud_permissions):
            return

        permissions = [
            cls(**data)
            for data in cls.get_model_crud_permissions(table, plural_table=plural_table)
        ]
        return await Permission.batch_create(permissions)
