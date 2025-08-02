from apps.user.dependencies.access import UserAccess


class AdminAccess(UserAccess):
    def test_access(self) -> bool:
        return self.user.is_admin


class StaffAccess(UserAccess):
    def test_access(self) -> bool:
        return self.user.is_admin


class ActiveAccess(UserAccess):
    def test_access(self) -> bool:
        return self.user.is_admin
