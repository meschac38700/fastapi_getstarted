from .chat import routers
from .message import routers as message_routers
from .room import routers as room_routers

routers.include_router(room_routers, prefix="/rooms", tags=["chat", "room"])
routers.include_router(message_routers, prefix="/messages", tags=["chat", "message"])

__all__ = ["routers"]
