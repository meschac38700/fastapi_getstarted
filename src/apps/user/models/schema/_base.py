from pydantic import Field

from apps.user.models import User
from apps.user.models._base import UserBase
from apps.user.utils.types import UserRole


class UserBaseModel(UserBase):
    role: UserRole = Field(default=UserRole.active)

    def role_guard(self, stored_user: User, auth_user: User):
        """Reset role if changed and the current user is not admin."""

        role_changed = stored_user.role != self.role
        if role_changed and not auth_user.is_admin:
            self.role = stored_user.role

    class ConfigDict:
        from_attributes = True
