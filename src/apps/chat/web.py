from typing import Annotated

from fastapi import APIRouter, Depends, Request
from starlette.websockets import WebSocket

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.models.orm import ChatRoom
from apps.chat.services.manager import ChatWebSocketManager
from apps.user.models.user import User
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")

websocket_manager = ChatWebSocketManager()


@routers.get(
    "/",
    name="chat-template",
)
async def chat(request: Request):
    query = await ChatRoom.all()
    return render(request, "chat/index.html", {"rooms": query})


@routers.websocket(
    "/{room_id}/",
    name="room-websocket",
)
async def chat_room(
    websocket: WebSocket,
    room_id: int,
    auth_user: Annotated[User, Depends(current_user)],
):
    room = await ChatRoom.get_or_404(id=room_id)
    await websocket_manager.init_connection(websocket, room, auth_user)
