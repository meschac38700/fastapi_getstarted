from fastapi import APIRouter, Request
from starlette.websockets import WebSocket

from apps.chat.models import ChatRoom
from apps.chat.services.manager import WebSocketManager
from apps.user.models import User
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")

websocket_manager = WebSocketManager()


@routers.get("/")
def room_list(request: Request):
    return render(request, "chat/index.html")


@routers.websocket("/{room_name}/")
async def websocket_room(websocket: WebSocket, room_name: str):
    user = await User.first()
    room = await ChatRoom.get_or_404(name=room_name)
    await websocket_manager.init_connection(websocket, room=room, user=user)
