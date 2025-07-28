from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.dependencies.access import (
    ChatRoomAccess,
    ChatRoomDeleteAccess,
    ChatRoomEditAccess,
)
from apps.chat.dependencies.db import RoomDepends
from apps.chat.models import ChatRoom
from apps.chat.models.schemas.room import ChatRoomCreate, ChatRoomUpdate
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


@routers.patch(
    "/{room_id}/subscribe/",
    name="room-subscribe",
)
async def room_subscription(
    room: Annotated[ChatRoom, Depends(RoomDepends())],
    auth_user: User = Depends(current_user),
):
    if auth_user not in room.members:
        room.members.append(auth_user)
        await room.save()

    return {"success": True}


@routers.patch(
    "/{room_id}/unsubscribe/",
    name="room-unsubscribe",
)
async def room_unsubscription(
    room: Annotated[ChatRoom, Depends(RoomDepends())],
    auth_user: User = Depends(current_user),
):
    if auth_user in room.members:
        room.members.remove(auth_user)
        await room.save()

    return {"success": True}


@routers.post(
    "/",
    name="room-create",
    status_code=status.HTTP_201_CREATED,
)
async def create_room(
    room_data: ChatRoomCreate, auth_user: User = Depends(current_user)
):
    try:
        room = await ChatRoom(**room_data.model_dump(), owner_id=auth_user.id).save()
        return ChatRoom.model_validate(room)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Chat room already exists."
        ) from e


@routers.patch(
    "/{room_id}/",
    name="room-edit",
    status_code=status.HTTP_200_OK,
)
async def edit_room(
    room: Annotated[ChatRoom, Depends(ChatRoomEditAccess())],
    chat_room_data: ChatRoomUpdate,
):
    room.update_from_dict(chat_room_data.model_dump())
    await room.save()
    return ChatRoom.model_validate(room)


@routers.delete(
    "/{room_id}/",
    name="room-delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room(room: Annotated[ChatRoom, Depends(ChatRoomDeleteAccess())]):
    return await room.delete()
