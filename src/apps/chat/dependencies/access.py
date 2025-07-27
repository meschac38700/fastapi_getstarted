from fastapi import Depends, HTTPException, status

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.models import ChatMessage, ChatRoom
from apps.user.models import User
from core.db.query.exceptions import ObjectNotFoundError
from core.routers.dependencies import AccessDependency


class ChatRoomAccess(AccessDependency[ChatRoom]):
    room: ChatRoom
    user: User

    def test_access(self) -> bool:
        return self.user.is_admin or self.is_chat_owner() or self.is_member()

    def is_member(self):
        return self.user in self.room.members

    def is_chat_owner(self):
        return self.user == self.room.owner

    async def __call__(
        self, room_id: int, user: User = Depends(current_user())
    ) -> ChatRoom:
        try:
            self.room = await ChatRoom.get_or_404(id=room_id)
        except ObjectNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e

        self.user = user
        if not self.test_access():
            self.raise_access_denied()
        return self.room


class ChatRoomEditAccess(ChatRoomAccess):
    def test_access(self) -> bool:
        return self.user.is_admin or self.is_chat_owner()


class ChatMessageAccess(AccessDependency[ChatRoom]):
    def test_access(self) -> bool:
        return self.user.is_admin or self.is_room_owner() or self.is_message_author()

    def is_room_owner(self):
        return self.room.owner == self.user

    def is_message_author(self):
        return self.user.id == self.message.author_id

    async def __call__(
        self, room_id: int, message_id: int, user: User = Depends(current_user())
    ) -> ChatMessage:
        try:
            self.room = await ChatRoom.get_or_404(id=room_id)
            self.message = await ChatMessage.get_or_404(id=message_id)
        except ObjectNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e

        self.user = user
        if not self.test_access():
            self.raise_access_denied()
        return self.message


class ChatMessageDeleteAccess(ChatMessageAccess):
    def test_access(self) -> bool:
        return self.user.is_admin or self.is_message_author()
