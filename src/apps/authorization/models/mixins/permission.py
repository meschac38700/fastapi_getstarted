from typing import Iterable

from apps.authorization.models.permission import Permission


class PermissionMixin:
    def has_permissions(
        self, permissions: Iterable[Permission], any_match: bool = False
    ) -> bool:
        """all listed permissions"""
        if not permissions:
            return False

        if any_match:
            return any(perm in self.get_permissions() for perm in permissions)

        return all(perm in self.get_permissions() for perm in permissions)

    def get_permissions(self) -> set[Permission]:
        """Get all permissions linked to the current user/group"""
        permissions = getattr(self, "permissions", [])
        return permissions

    async def add_permission(self, permission: Permission):
        self.permissions.append(permission)
        await self.save()

    async def extend_permissions(self, permissions: Iterable[Permission]):
        self.permissions.extend(
            permission
            for permission in permissions
            if permission not in self.permissions
        )
        await self.save()

    async def remove_permissions(self, permissions: Iterable[Permission]):
        setattr(
            self,
            "permissions",
            [perm for perm in self.get_permissions() if perm not in permissions],
        )
        await self.save()
