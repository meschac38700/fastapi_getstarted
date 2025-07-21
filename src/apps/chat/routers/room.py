from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select

from apps.chat.models import ChatRoom
from apps.user.dependencies.roles import AdminAccess
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
