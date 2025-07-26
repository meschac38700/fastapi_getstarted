from sqlmodel import Field

from core.db import SQLTable


class ChatRoomUserLink(SQLTable, table=True):
    room_id: int | None = Field(
        default=None, foreign_key="chatroom.id", primary_key=True, ondelete="CASCADE"
    )
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        primary_key=True,
        ondelete="CASCADE",
    )
