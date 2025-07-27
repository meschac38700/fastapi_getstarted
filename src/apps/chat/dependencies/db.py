from fastapi import HTTPException, status

from apps.chat.models import ChatRoom
from core.db.query.exceptions import ObjectNotFoundError


class RoomDepends:
    async def __call__(self, room_id: int):
        try:
            room: ChatRoom = await ChatRoom.get_or_404(id=room_id)
            return room
        except ObjectNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e
