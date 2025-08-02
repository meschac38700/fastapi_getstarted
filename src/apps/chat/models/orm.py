from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from apps.chat.models.base import ChatMessageBaseModel, ChatRoomBaseModel
from apps.chat.models.relation_links import ChatRoomUserLink
from apps.user.models import User
from core.db.mixins import BaseTable


class ChatRoom(ChatRoomBaseModel, BaseTable, table=True):
    __table_args__ = (UniqueConstraint("name", "owner_id", name="chatroom_owner_id"),)

    owner_id: int | None = Field(
        foreign_key="users.id", default=None, ondelete="CASCADE"
    )
    owner: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    messages: list["ChatMessage"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "order_by": "asc(ChatMessage.created_at)",
        },
        back_populates="room",
    )
    members: list[User] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, link_model=ChatRoomUserLink
    )

    async def subscribe(self, member: User):
        self.members.append(member)
        return await self.save()

    async def unsubscribe(self, member: User):
        self.members.remove(member)
        return await self.save()


class ChatMessage(ChatMessageBaseModel, BaseTable, table=True):
    author_id: int | None = Field(
        foreign_key="users.id", default=None, ondelete="SET NULL"
    )
    author: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    room_id: int | None = Field(
        foreign_key="chatroom.id", default=None, ondelete="CASCADE"
    )
    room: ChatRoom = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="messages"
    )
