from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from app.database import async_session
from app.models import Organization
from app.services.websocket_manager import ws_manager
import asyncio

router = APIRouter()

@router.websocket("/ws/{api_key}")
async def websocket_endpoint(ws: WebSocket, api_key: str):
    async with async_session() as db:
        result = await db.execute(select(Organization).where(Organization.api_key == api_key))
        org = result.scalar_one_or_none()
        if not org:
            await ws.close(code=4001)
            return
        await ws_manager.connect(api_key, ws)
        ping_task = asyncio.create_task(ws_manager.keepalive(api_key, ws))
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            ping_task.cancel()
            ws_manager.disconnect(api_key, ws)
