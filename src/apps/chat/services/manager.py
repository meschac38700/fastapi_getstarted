import json
import logging
from typing import Any, Awaitable, Callable, Literal, ParamSpec, TypedDict

import anyio
from anyio import CancelScope, Event
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


class ConnectionState(TypedDict):
    user: User | None
    current_room: ChatRoom | None
    sender_scope: CancelScope | None
    room_event: Event | None


class MessagePayload(TypedDict):
    action: Literal["send", "change_room"]
    message: str | None
    room_id: int | None  # depends on the action


class ChatWebSocketManager(metaclass=Singleton):
    def __init__(self, p_logger: logging.Logger | None = None):
        self.logger = p_logger or _logger
        self.broadcaster = Broadcast(settings.celery_broker)

    async def init_connection(self, websocket: WebSocket, author: User):
        await websocket.accept()
        connection_state: ConnectionState = {
            "current_room": None,
            "sender_scope": None,
            "user": author,
            "room_event": anyio.Event(),
        }

        async with anyio.create_task_group() as tg:
            tg.start_soon(self._receiver_handler, websocket, connection_state, tg)
            tg.start_soon(self._sender_handler, websocket, connection_state, tg)

    async def _receiver_handler(
        self, websocket: WebSocket, state: ConnectionState, task_group: TaskGroup
    ):
        async def _receiver():
            async for raw_message in websocket.iter_text():
                message_payload = self._process_raw_message(raw_message, state)
                if message_payload["action"] == "send":
                    await self._publish_message(message_payload["message"], state)
                elif message_payload["action"] == "change_room":
                    await self._switch_room(int(message_payload["room_id"]), state)

        await self._exception_handler(_receiver, task_group=task_group)

    async def _sender_handler(
        self, websocket: WebSocket, state: ConnectionState, task_group: TaskGroup
    ):
        async def _sender():
            while True:
                # wait for user to switch a room
                await state["room_event"].wait()
                room = state["current_room"]
                # set new room event for next room switch
                state["room_event"] = anyio.Event()

                self.logger.info("Subscribing to room %s", room.name)
                async with self.broadcaster.subscribe(channel=room.name) as sub:
                    with anyio.CancelScope() as cancel_scope:
                        state["sender_scope"] = cancel_scope
                        async for event in sub:
                            await websocket.send_json(event.message)

        await self._exception_handler(_sender, task_group=task_group)

    async def _publish_message(self, msg: str, state: ConnectionState):
        room = state["current_room"]
        msg_data = await self._save_message(msg, state)
        await self.broadcaster.publish(channel=room.name, message=json.dumps(msg_data))

    def _process_raw_message(
        self, raw_message: str, state: ConnectionState
    ) -> MessagePayload:
        try:
            message_dict = json.loads(raw_message)
            return MessagePayload(**message_dict)
        except json.decoder.JSONDecodeError as e:
            self.logger.error("Invalid JSON message: %s", raw_message, exc_info=e)
        return MessagePayload(
            message=raw_message,
            action="send",
            room_id=state["current_room"].id,
        )

    async def _switch_room(self, room_id: int, state: ConnectionState):
        self.logger.info("Switching room %s", room_id)
        state["current_room"] = await ChatRoom.get(id=room_id)
        if state["sender_scope"] is not None:
            state["sender_scope"].cancel()

        room = state["current_room"]
        username = state["user"].username
        self.logger.info("User %s switched to room %s", username, room.name)
        # release event for send handler to process
        state["room_event"].set()

    async def _exception_handler(self, callback: Fn, *args, task_group: TaskGroup):
        try:
            await callback(*args)
        except WebSocketDisconnect as e:
            self.logger.info("WebSocket: Client disconnected %s", e)

        except Exception as e:
            self.logger.exception("WebSocket: Exception %s", e)
        finally:
            task_group.cancel_scope.cancel()

    async def _save_message(self, message: str, state: ConnectionState):
        """Persist the given message in the database."""
        room_id = state["current_room"].id
        user_id = state["user"].id
        _msg_obj = await ChatMessage(
            content=message, room_id=room_id, author_id=user_id
        ).save()
        return _msg_obj.model_dump(mode="json")
