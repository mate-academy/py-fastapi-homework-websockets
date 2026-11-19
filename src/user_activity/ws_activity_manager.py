from asyncio import Lock
from typing import Dict, List

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from schemas.user_activity import UserActivitySchema
from user_activity.interfaces import UserActivityWebSocketManagerInterface


class UserActivityWebSocketManager(UserActivityWebSocketManagerInterface):
    """In-memory implementation of the WebSocket connection manager for user activity tracking."""

    def __init__(self) -> None:
        """Initialize an empty mapping of user IDs to their active WebSocket connections."""
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self._connection_lock = Lock()

    def connection_lock(self) -> Lock:
        return self._connection_lock

    async def connect(self, websocket: WebSocket, user_data: UserActivitySchema) -> None:
        """
        Register a new WebSocket connection for a user and broadcast a
        "user_connected" event if this is the user's first active connection.

        Args:
            websocket (WebSocket): The WebSocket connection to register.
            user_data (UserActivitySchema): The connecting user's activity data.

        Returns:
            None
        """
        connections = self.active_connections.setdefault(user_data.user_id, [])
        connections.append(websocket)
        if len(connections) == 1:
            await self._broadcast(
                {"event": "user_connected", "user": user_data.model_dump(mode="json")},
                exclude=user_data.user_id,
            )

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection for a user and broadcast a
        "user_disconnected" event once the user has no active connections left.

        Args:
            user_id (int): The ID of the disconnecting user.
            websocket (WebSocket): The WebSocket connection to remove.

        Returns:
            None
        """
        connections = self.active_connections.get(user_id)
        if connections is None or websocket not in connections:
            return
        connections.remove(websocket)
        if not connections:
            del self.active_connections[user_id]
            await self._broadcast({"event": "user_disconnected", "user_id": user_id})

    async def _broadcast(self, message: dict, exclude: int = None) -> None:
        """
        Send a message to all connected users, optionally skipping one user.

        Args:
            message (dict): The message payload to broadcast.
            exclude (Optional[int]): User ID to exclude from the broadcast, if any.

        Returns:
            None
        """
        recipients = [
            websocket
            for user_id, connections in self.active_connections.items()
            if user_id != exclude
            for websocket in connections
        ]
        await self._send_to_connections(message, recipients)

    async def send_personal_message(self, message: dict, user_id: int) -> None:
        """
        Send a message to all active connections belonging to a single user.

        Args:
            message (dict): The message payload to send.
            user_id (int): The ID of the target user.

        Returns:
            None
        """
        recipients = self.active_connections.get(user_id, []).copy()
        await self._send_to_connections(message, recipients)

    @staticmethod
    async def _send_to_connections(message: dict, recipients: List[WebSocket]) -> None:
        for websocket in recipients:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                # The receiving service cleans up this connection when it disconnects.
                continue
            except RuntimeError:
                if WebSocketState.DISCONNECTED not in (websocket.client_state, websocket.application_state):
                    raise
