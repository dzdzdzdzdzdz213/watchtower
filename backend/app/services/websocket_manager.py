from fastapi import WebSocket
from collections import defaultdict
import json
import asyncio
from typing import Set

class WSManager:
    def __init__(self):
        self.connections: dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, api_key: str, ws: WebSocket):
        await ws.accept()
        self.connections[api_key].add(ws)
        await ws.send_text(json.dumps({"type": "connected", "message": "WatchTower WebSocket connected"}))

    def disconnect(self, api_key: str, ws: WebSocket):
        self.connections[api_key].discard(ws)
        if not self.connections[api_key]:
            del self.connections[api_key]

    async def broadcast(self, api_key: str, message: dict):
        dead = set()
        for ws in self.connections.get(api_key, set()):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(api_key, ws)

    async def keepalive(self, api_key: str, ws: WebSocket):
        try:
            while True:
                await asyncio.sleep(30)
                await ws.send_text(json.dumps({"type": "ping"}))
        except Exception:
            pass

ws_manager = WSManager()
