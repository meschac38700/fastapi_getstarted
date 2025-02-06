from fastapi import APIRouter

from .groups import routers as group_routers
from .permissions import routers as permission_routers

routers = APIRouter(tags=["Authorization"], prefix="/authorizations")
routers.include_router(permission_routers, prefix="/permissions")
routers.include_router(group_routers, prefix="/groups")

__all__ = ["routers"]
