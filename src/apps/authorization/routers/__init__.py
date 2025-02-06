from fastapi import APIRouter

from .permissions import routers as permission_routers

routers = APIRouter(tags=["Authorization"], prefix="/authorizations")
routers.include_router(permission_routers, prefix="/permissions")

__all__ = ["routers"]
