from core.db import SQLTable


class ChatRoomBaseModel(SQLTable):
    name: str


class ChatMessageBaseModel(SQLTable):
    content: str
