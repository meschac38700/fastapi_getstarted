from sqlmodel import Field, Relationship

from apps.chat.models.base import ChatMessageBaseModel, ChatRoomBaseModel
from apps.user.models import User
from core.db.mixins import BaseTable


class ChatRoom(ChatRoomBaseModel, BaseTable, table=True):
    owner_id: int = Field(foreign_key="users.id", default=None, ondelete="CASCADE")
    owner: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    messages: list["ChatMessage"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    members: list[User] = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class ChatMessage(ChatMessageBaseModel, BaseTable, table=True):
    author_id: int = Field(foreign_key="users.id", default=None, ondelete="CASCADE")
    author: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    room_id: int = Field(foreign_key="chatroom.id", default=None, ondelete="CASCADE")
    room: ChatRoom = Relationship(sa_relationship_kwargs={"lazy": "joined"})
