from functools import lru_cache


class PermissionMixin:
    def has_permission(self, permissions: list[str]) -> bool:
        """any listed permissions == one or more listed permissions"""
        return len(self.get_permissions().intersection(permissions)) > 0

    def has_permissions(self, permission: list[str]) -> bool:
        """all listed permissions"""
        return self.get_permissions() == set(permission)

    @lru_cache
    def get_permissions(self) -> set[str]:
        """Get all permissions linked to the current user/group"""
        permissions = getattr(self, "permissions", [])
        return {permission.name for permission in permissions}
