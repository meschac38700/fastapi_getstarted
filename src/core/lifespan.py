from sqlalchemy.ext.asyncio import AsyncEngine

from apps.chat.services.manager import WebSocketManager

websocket_manager = WebSocketManager()


async def setup(_: AsyncEngine):
    """Script to be run after fastapi setup."""
    await websocket_manager.broadcast.connect()


async def teardown(_: AsyncEngine):
    """Script to be run before fastapi shutdown."""
    await websocket_manager.broadcast.disconnect()
