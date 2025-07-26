from fastapi import APIRouter, Request
from starlette.websockets import WebSocket

from apps.chat.models.orm import ChatMessage, ChatRoom
from apps.chat.services.manager import ChatWebSocketManager
from apps.user.models.user import User
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")

websocket_manager = ChatWebSocketManager()


@routers.get("/")
async def chat(request: Request):
    messages = await ChatMessage.all()
    return render(request, "chat/index.html", {"messages": messages})


@routers.websocket("/{room_name}/")
async def chat_room(websocket: WebSocket, room_name: str):
    # mock author
    author = await User.first()
    room = await ChatRoom.get_or_404(name=room_name)
    await websocket_manager.init_connection(websocket, room, author)
