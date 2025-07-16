from core.db.mixins import BaseTable

from ._base import PermissionBase
from .mixins import CRUDModelMixin


class Permission(CRUDModelMixin, BaseTable, PermissionBase, table=True):
    pass
