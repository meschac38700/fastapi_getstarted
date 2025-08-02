import abc
from abc import abstractmethod

from fastapi import HTTPException, status


class AccessDependency[T](abc.ABC):
    detail = "Insufficient rights to carry out this action"

    @abstractmethod
    def test_access(self) -> bool:
        pass

    def raise_access_denied(self):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=self.detail)
