from abc import ABC, abstractmethod
from http import HTTPStatus

from fastapi import Depends, HTTPException

from apps.authentication.dependencies.oauth2 import current_user
from apps.user.models import User


class RoleAccess(ABC):
    @abstractmethod
    def _has_access(self, user: User) -> bool:
        pass

    async def __call__(self, user: User = Depends(current_user())):
        allowed = self._has_access(user)

        if not allowed:
            detail = "Your role does not allow you to do this action"
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return allowed


class AdminAccess(RoleAccess):
    def _has_access(self, user: User) -> bool:
        return user.is_admin


class StaffAccess(RoleAccess):
    def _has_access(self, user: User) -> bool:
        return user.is_admin


class ActiveAccess(RoleAccess):
    def _has_access(self, user: User) -> bool:
        return user.is_admin
