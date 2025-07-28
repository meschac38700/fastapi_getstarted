from fastapi import APIRouter, Request
from starlette.websockets import WebSocket

from apps.chat.models.orm import ChatRoom
from apps.chat.services.manager import ChatWebSocketManager
from apps.user.models.user import User
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")

websocket_manager = ChatWebSocketManager()


@routers.get("/", name="chat-template")
async def chat(request: Request):
    query = await ChatRoom.all()
    return render(request, "chat/index.html", {"rooms": query})


@routers.websocket("/{room_id}/", name="room-websocket")
async def chat_room(websocket: WebSocket, room_id: int):
    # mock author
    author = await User.first()
    room = await ChatRoom.get_or_404(id=room_id)
    await websocket_manager.init_connection(websocket, room, author)
