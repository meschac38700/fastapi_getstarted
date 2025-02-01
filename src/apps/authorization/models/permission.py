from sqlmodel import Field

from ._base import PermissionBase
from .utils import CRUDModelMixin


class Permission(CRUDModelMixin, PermissionBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
