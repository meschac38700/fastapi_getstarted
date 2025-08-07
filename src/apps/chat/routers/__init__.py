from .message import routers as message_routers
from .room import routers as room_routers

room_routers.include_router(
    message_routers, prefix="/{room_id}/messages", tags=["chat", "message"]
)

__all__ = ["room_routers"]
