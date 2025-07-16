import asyncio

from apps.authorization.models import Permission
from apps.user.models import User
from core.db.fixtures.model_loaders.base import ModelBaseLoader
from core.db.fixtures.utils import ModelDataType


class UserLoader(ModelBaseLoader[User]):
    async def _fix_permissions(self, instance: User) -> User:
        """Replace permission names to permission instances."""
        if permission_names := set(instance.permissions):
            permissions = await Permission.filter(name__in=permission_names)
            if len(permissions) != len(permission_names):
                missing_perms = [
                    perm.name for perm in permissions if perm.name in permission_names
                ] or permission_names
                raise ValueError(f"Permissions not found: {missing_perms}")

            instance.permissions = permissions
        return instance

    async def load(self, data_list: list[ModelDataType]):
        instances = self._to_instances(data_list)
        instances = await asyncio.gather(
            *[self._fix_permissions(instance) for instance in instances]
        )
        await User.bulk_create_or_update(instances)
