from fastapi import Depends, HTTPException, status

from apps.authentication.dependencies.oauth2 import current_user
from apps.chat.models import ChatRoom
from apps.user.models import User
from core.db.query.exceptions import ObjectNotFoundError
from core.routers.dependencies import AccessDependency


class ChatRoomAccess(AccessDependency[ChatRoom]):
    room: ChatRoom
    user: User

    def test_access(self) -> bool:
        is_owner = self.room.owner == self.user
        return self.user.is_admin or is_owner

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
