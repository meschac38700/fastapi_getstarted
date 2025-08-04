from fastapi import APIRouter, Depends, Request
from starlette.websockets import WebSocket

from apps.authentication.dependencies.oauth2 import (
    current_session_user,
    current_user,
)
from apps.chat.models.orm import ChatRoom
from apps.chat.services.manager import ChatWebSocketManager
from apps.user.models.user import User
from core.db.dependencies import SessionDep
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")

websocket_manager = ChatWebSocketManager()


@routers.get(
    "/",
    name="chat-template",
)
async def chat(
    request: Request, db: SessionDep, auth_user: User = Depends(current_user)
):
    rooms = await ChatRoom.get_member_rooms(db, auth_user.id)
    return render(request, "chat/index.html", {"rooms": rooms})


@routers.websocket(
    "/{room_id}/",
    name="room-websocket",
)
async def chat_room(
    websocket: WebSocket,
    room_id: int,
):
    author = await current_session_user(websocket)
    room = await ChatRoom.get_or_404(id=room_id)
    await websocket_manager.init_connection(websocket, room, author)


@routers.get(
    "/filter/rooms/",
    name="room-filter",
    description="Filter rooms by name",
)
async def filter_rooms(
    db: SessionDep,
    room_name: str | None = None,
    auth_user: User = Depends(current_user),
):
    """Filter rooms by name."""
    if room_name is None:
        return await ChatRoom.get_member_rooms(db, auth_user.id)

    if auth_user.is_admin:
        return await ChatRoom.filter(name__istartswith=room_name)

    return await ChatRoom.get_member_rooms(
        db, auth_user.id, filters={"name__istartswith": room_name}
    )
