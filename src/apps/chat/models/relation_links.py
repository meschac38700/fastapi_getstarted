from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from core.db import SQLTable


class ChatRoomUserLink(SQLTable, table=True):
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="chatroom_user_id"),)
    room_id: int | None = Field(
        default=None, foreign_key="chatroom.id", primary_key=True, ondelete="CASCADE"
    )
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        primary_key=True,
        ondelete="CASCADE",
    )
