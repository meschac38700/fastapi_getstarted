import enum


class UserRole(enum.Enum):
    admin = "admin"
    staff = "staff"
    active = "active"

    def __str__(self):
        return self.value
