from sqlmodel import Field, Relationship

from apps.chat.models.base import ChatMessageBaseModel, ChatRoomBaseModel
from apps.user.models import User
from core.db.mixins import BaseTable


class ChatRoom(ChatRoomBaseModel, BaseTable, table=True):
    owner_id: int | None = Field(
        foreign_key="users.id", default=None, ondelete="SET NULL"
    )
    owner: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    messages: list["ChatMessage"] = Relationship(
        back_populates="room",
    )
    members: list[User] = Relationship(
        sa_relationship_kwargs={"lazy": "joined", "overlaps": "owner"}
    )

    async def subscribe(self, member: User):
        self.members.append(member)
        return await self.save()

    async def unsubscribe(self, member: User):
        self.members.remove(member)
        return await self.save()


class ChatMessage(ChatMessageBaseModel, BaseTable, table=True):
    author_id: int | None = Field(
        foreign_key="users.id", default=None, ondelete="CASCADE"
    )
    author: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    room_id: int | None = Field(
        foreign_key="chatroom.id", default=None, ondelete="CASCADE"
    )
    room: ChatRoom = Relationship(back_populates="messages")
