import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field

from apps.chat.models.utils import ChatVisibility
from core.db import SQLTable


class ChatRoomBaseModel(SQLTable):
    name: str
    visibility: ChatVisibility = Field(
        default=ChatVisibility.private,
        sa_column=sa.Column(
            postgresql.ENUM(ChatVisibility, name="visibility"),
            default=ChatVisibility.private,
            index=True,
        ),
    )


class ChatMessageBaseModel(SQLTable):
    content: str
