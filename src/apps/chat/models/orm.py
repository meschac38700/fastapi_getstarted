from typing import Any

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, col, or_, select

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

    @classmethod
    async def get_member_rooms(
        cls, session: AsyncSession, user: User, *, filters: dict["str", Any] = None
    ):
        """Retrieve all rooms where the current user is a member of or owner of."""
        _additional_filters = cls.resolve_filters(**(filters or {}))
        statement = select(cls).outerjoin(
            ChatRoomUserLink, col(cls.id) == ChatRoomUserLink.room_id
        )
        if not user.is_admin:
            statement = statement.where(
                or_(
                    col(cls.visibility) == "public",
                    col(cls.owner_id) == user.id,
                    col(ChatRoomUserLink.user_id) == user.id,
                )
            )

        if filters:
            statement = statement.where(*_additional_filters)

        statement = (
            statement.options(selectinload(col(cls.members)))
            .distinct()
            .order_by(col(cls.updated_at).desc())
        )
        res = await session.execute(statement)
        results = res.scalars().unique().all()
        return results


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
