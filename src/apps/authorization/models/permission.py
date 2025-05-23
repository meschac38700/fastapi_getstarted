from sqlmodel import Field

from ._base import PermissionBase
from .mixins import CRUDModelMixin


class Permission(CRUDModelMixin, PermissionBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
