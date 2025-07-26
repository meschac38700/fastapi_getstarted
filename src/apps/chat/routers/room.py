from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.dependencies.access import ChatRoomAccess
from apps.chat.models import ChatMessage, ChatRoom
from apps.chat.models.schemas.message import ChatMessageCreate
from apps.user.dependencies.roles import AdminAccess
from apps.user.models import User
from core.db.dependencies import SessionDep

routers = APIRouter()


@routers.get("/", name="room-all", dependencies=[Depends(AdminAccess())])
async def get_rooms(db: SessionDep) -> Page[ChatRoom]:
    """Get all rooms.

    The following approach is raising a warning
    since fastapi_pagination does not support async queries yet:

        from fastapi_pagination.ext.sqlalchemy import apaginate
        query = select(ChatRoom).order_by(ChatRoom.created_at)
        return await apaginate(db, query)

    Issue: https://github.com/langflow-ai/langflow/issues/7951
    DeprecationWarning:
       🚨 You probably want to use `session.exec()` instead of `session.execute()`.
       This is the original SQLAlchemy `session.execute()` method that returns objects
       of type `Row`, and that you have to call `scalars()` to get the model objects.
    """
    query = select(ChatRoom).order_by(ChatRoom.created_at)
    return await apaginate(db, query)


@routers.get("/{room_id}/", name="room-get")
def get_room(room: Annotated[ChatRoom, Depends(ChatRoomAccess())]) -> ChatRoom:
    return room


@routers.get("/{room_id}/messages/", name="room-messages")
async def get_room_messages(
    db: SessionDep, room: Annotated[ChatRoom, Depends(ChatRoomAccess())]
) -> Page[ChatMessage]:
    query = (
        select(ChatMessage)
        .where(ChatMessage.room_id == room.id)
        .order_by(ChatMessage.created_at)
    )
    return await apaginate(db, query)


@routers.post("/{room_id}/messages/", name="room-message-add")
async def add_message_to_room(
    message: ChatMessageCreate,
    room: Annotated[ChatRoom, Depends(ChatRoomAccess())],
    auth_user: User = Depends(current_user()),
):
    return await ChatMessage(
        **message.model_dump(), author_id=auth_user.id, room_id=room.id
    ).save()
