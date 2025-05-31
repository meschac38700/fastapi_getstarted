import enum


class BaseEnum(enum.Enum):
    def __str__(self):
        return self.value


class UserRole(BaseEnum):
    admin = "admin"
    staff = "staff"
    active = "active"


class UserStatus(BaseEnum):
    active = "active"
    inactive = "inactive"
