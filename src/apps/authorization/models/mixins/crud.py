from typing import Any, Literal

CRUDPermissions = Literal["create", "read", "update", "delete"]


class CRUDModelMixin:
    # permission name format: {http verb}{separator}{model name}
    _PERMISSION_NAME_SEPARATOR = ":"

    @classmethod
    def format_permission_name(cls, method: str | CRUDPermissions, target_table: str):
        return f"{method}{cls._PERMISSION_NAME_SEPARATOR}{target_table}"

    @classmethod
    def get_object_crud_names(cls, target_table: str):
        return (
            f"{method}_{target_table}"
            for method in ["create", "read", "update", "delete"]
        )

    @classmethod
    def get_crud_data_list(
        cls, target_table: str, *, raw_sql: bool = False
    ) -> list[dict[str, Any]] | str:
        crud_methods = ["create", "read", "update", "delete"]

        description = "This {0} allows user to {1} the {2} model."
        kwargs_list = [
            {
                "name": cls.format_permission_name(method, target_table),
                "description": description.format(
                    cls.table_name(), method, target_table.title()
                ),
                "display_name": f"{method.title()} {target_table}",
                "target_table": target_table,
            }
            for method in crud_methods
        ]

        if raw_sql:
            return cls._crud_items_sql(kwargs_list)

        return kwargs_list

    @classmethod
    def _crud_items_sql(cls, data_list: list[dict[str, Any]]) -> str:
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
    async def generate_crud_objects(cls, table: str):
        """Create items for the given table based of CRUD methods."""
        perm_name = cls.format_permission_name("read", table)
        if await cls.get(name=perm_name):
            return

        data_list = cls.get_crud_data_list(table)
        model_list = [cls(**kw) for kw in data_list]
        return await cls.bulk_create_or_update(model_list)
