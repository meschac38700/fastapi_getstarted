from fastapi import APIRouter, Depends, Request
from starlette.websockets import WebSocket

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.models import ChatRoom
from apps.user.models import User
from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")


@routers.get("/")
def room_list(request: Request):
    return render(request, "chat/index.html")


@routers.websocket("/{room_name}/")
async def websocket_room(
    websocket: WebSocket, room_name: str, _: User = Depends(current_user())
):
    _ = ChatRoom.get_or_404(name=room_name)

    await websocket.accept()
    # WIP listen on messages
