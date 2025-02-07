from fastapi import APIRouter

from .groups import routers as user_group_routers
from .permissions import routers as user_permission_routers
from .users import routers as user_routers

routers = APIRouter(tags=["Users"], prefix="/users")
routers.include_router(user_permission_routers)
routers.include_router(user_group_routers)
routers.include_router(user_routers)

__all__ = ["routers"]
