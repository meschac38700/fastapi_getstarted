from typing import Any

import sqlalchemy as sa

from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.authorization.models.relation_links import PermissionGroupLink

Data = list[dict[str, Any]]


class ManagePermissionMigration:
    """Manage permissions for new models when applying migrations."""

    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.permission_table = Permission.table_name()
        self.group_table = Group.table_name()

    def _table_exists(self, table_name: str) -> bool:
        return self.conn.engine.dialect.has_table(self.conn, table_name)

    def permission_table_exists(self) -> bool:
        return self._table_exists(self.permission_table)

    def group_table_exists(self) -> bool:
        return self._table_exists(self.group_table)

    def _build_permission_group_link_insert_query(
        self, permissions: Data, groups: Data
    ) -> str:
        query = f"""
        INSERT INTO {PermissionGroupLink.table_name()}(permission_name, group_name) VALUES
        """
        for i, perm_group in enumerate(zip(permissions, groups)):
            perm, group = perm_group
            val = (perm["name"], group["name"])
            if i > 0:
                query += f",\n {val}"
                continue
            query += f"{val}"
        return query + ";"

    def sql_select(self, table_name: str, *, where: str, order_by: str = "") -> Data:
        _order_by = f"ORDER BY {order_by}" if order_by else ""
        perms_statement = sa.text(f"""
            SELECT *
            FROM {table_name}
            WHERE {where}
            {_order_by};
        """)
        return self.conn.execute(perms_statement).mappings().all()

    def generate_permissions(self, target_table: str) -> Data:
        # Auto generate crud permissions for previously created model table
        perms_sql = Permission.get_crud_data_list(target_table, raw_sql=True)
        self.cursor.execute(perms_sql)
        return self.sql_select(
            self.permission_table,
            where=f"target_table='{target_table}'",
            order_by="name ASC",
        )

    def generate_groups(self, target_table: str) -> Data:
        # Auto generate crud groups for previously created model table
        groups_sql = Group.get_crud_data_list(target_table, raw_sql=True)
        self.cursor.execute(groups_sql)
        return self.sql_select(
            self.group_table,
            where=f"name LIKE '%_{target_table}'",
            order_by="name ASC",
        )

    def generate_permission_group_links(
        self, target_table: str, *, perms: Data, groups: Data
    ) -> None:
        # Auto generate permission group links
        if not self._table_exists(PermissionGroupLink.table_name()):
            return

        links = self.sql_select(
            PermissionGroupLink.table_name(),
            where=f"group_name LIKE '%_{target_table}'",
        )
        if links:
            return

        permission_group_link_sql = self._build_permission_group_link_insert_query(
            perms, groups
        )
        self.cursor.execute(permission_group_link_sql)
