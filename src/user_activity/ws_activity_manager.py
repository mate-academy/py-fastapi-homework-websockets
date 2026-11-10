from typing import Dict, List, Optional
from fastapi import WebSocket
from schemas import UserActivitySchema


class UserActivityWebSocketManager:
    def __init__(self):
        # Dict[user_id, List[WebSocket]]
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_data: UserActivitySchema) -> None:
        user_id = user_data.user_id
        is_first_connection = user_id not in self.active_connections or not self.active_connections[user_id]

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

        if is_first_connection:
            message = {
                "event": "user_connected",
                "user": user_data.model_dump(mode="json"),
            }
            await self._broadcast(message, exclude=user_id)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                message = {
                    "event": "user_disconnected",
                    "user_id": user_id,
                }
                await self._broadcast(message)

    async def _broadcast(self, message: dict, exclude: Optional[int] = None) -> None:

        for u_id, sockets in list(self.active_connections.items()):
            if u_id == exclude:
                continue
            for ws in list(sockets):
                try:
                    await ws.send_json(message)
                except Exception:
                    if ws in sockets:
                        sockets.remove(ws)

    async def send_personal_message(self, message: dict, user_id: int) -> None:

        if user_id in self.active_connections:
            for ws in list(self.active_connections[user_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    pass
