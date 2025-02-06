from fastapi import APIRouter

from .users import routers as user_routers

routers = APIRouter(tags=["users"], prefix="/users")
routers.include_router(user_routers)

__all__ = ["routers"]
