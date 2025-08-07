from sqlalchemy.ext.asyncio import AsyncEngine

from apps.chat.services.manager import ChatWebSocketManager

websocket_manager = ChatWebSocketManager()


async def setup(_: AsyncEngine):
    """Script to be run after fastapi setup."""
    await websocket_manager.broadcaster.connect()


async def teardown(_: AsyncEngine):
    """Script to be run before fastapi shutdown."""
    await websocket_manager.broadcaster.disconnect()
