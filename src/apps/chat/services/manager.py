import json
import logging
from typing import Any, Awaitable, Callable, ParamSpec

import anyio
from anyio.abc import TaskGroup
from broadcaster import Broadcast
from starlette.websockets import WebSocket, WebSocketDisconnect

from apps.chat.models.orm import ChatMessage, ChatRoom
from apps.user.models import User
from core.design.singleton import Singleton
from core.monitoring.logger import get_logger
from settings import settings

_logger = get_logger(__name__)

P = ParamSpec("P")
Fn = Callable[P, Awaitable[Any]]


class ChatWebSocketManager(metaclass=Singleton):
    def __init__(self, p_logger: logging.Logger | None = None):
        self.logger = p_logger or _logger
        self.broadcaster = Broadcast(settings.celery_broker)

    async def init_connection(self, websocket: WebSocket, room: ChatRoom, author: User):
        await websocket.accept()

        async with anyio.create_task_group() as tg:
            tg.start_soon(self._receiver_handler, websocket, room, author, tg)
            tg.start_soon(self._sender_handler, websocket, room, tg)

    async def _receiver_handler(
        self, websocket: WebSocket, room: ChatRoom, author: User, task_group: TaskGroup
    ):
        async def _receiver():
            async for message in websocket.iter_text():
                msg_data = await self._save_message(message, room.id, author.id)
                await self.broadcaster.publish(
                    channel=room.name, message=json.dumps(msg_data)
                )

        await self._exception_handler(_receiver, task_group=task_group)

    async def _sender_handler(
        self, websocket: WebSocket, room: ChatRoom, task_group: TaskGroup
    ):
        async def _sender():
            async with self.broadcaster.subscribe(channel=room.name) as sub:
                async for event in sub:
                    await websocket.send_json(event.message)

        await self._exception_handler(_sender, task_group=task_group)

    async def _exception_handler(self, callback: Fn, *args, task_group: TaskGroup):
        try:
            await callback(*args)
        except WebSocketDisconnect as e:
            self.logger.info("WebSocket: Client disconnected %s", e)

        except Exception as e:
            self.logger.exception("WebSocket: Exception %s", e)
        finally:
            task_group.cancel_scope.cancel()

    async def _save_message(self, message: str, room_id: int, user_id: int):
        """Persist the given message in the database."""
        _msg_obj = await ChatMessage(
            content=message, room_id=room_id, author_id=user_id
        ).save()
        return _msg_obj.model_dump(mode="json")
