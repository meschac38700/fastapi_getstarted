from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.dependencies.access import (
    ChatMessageDeleteAccess,
    ChatRoomAccess,
)
from apps.chat.models import ChatMessage, ChatRoom
from apps.chat.models.schemas.message import ChatMessageCreate
from apps.user.models import User
from core.db.dependencies import SessionDep

routers = APIRouter()


@routers.get("/", name="room-messages")
async def get_room_messages(
    db: SessionDep, room: Annotated[ChatRoom, Depends(ChatRoomAccess())]
) -> Page[ChatMessage]:
    query = (
        select(ChatMessage)
        .where(ChatMessage.room_id == room.id)
        .order_by(ChatMessage.created_at)
    )
    return await apaginate(db, query)


@routers.post("/", name="room-message-add")
async def add_room_message(
    message: ChatMessageCreate,
    room: Annotated[ChatRoom, Depends(ChatRoomAccess())],
    auth_user: User = Depends(current_user()),
):
    return await ChatMessage(
        **message.model_dump(), author_id=auth_user.id, room_id=room.id
    ).save()


@routers.delete(
    "/{message_id}/",
    name="room-message-delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room_message(
    message: Annotated[ChatMessage, Depends(ChatMessageDeleteAccess())],
):
    return await message.delete()
