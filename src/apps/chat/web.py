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
