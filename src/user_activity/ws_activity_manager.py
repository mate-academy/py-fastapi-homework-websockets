from fastapi import WebSocket
from typing import Dict, List

from schemas.user_activity import UserActivitySchema
from user_activity.interfaces import UserActivityWebSocketManagerInterface


class UserActivityWebSocketManager(UserActivityWebSocketManagerInterface):
    """In-memory implementation of the WebSocket connection manager for user activity tracking."""

    def __init__(self) -> None:
        """Initialize an empty mapping of user IDs to their active WebSocket connections."""
        self.active_connections: Dict[int, List[WebSocket]] = {}

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
        self.active_connections.setdefault(user_data.user_id, []).append(websocket)
        if len(self.active_connections[user_data.user_id]) == 1:
            await self._broadcast(
                {
                    "event": "user_connected",
                    "user": user_data.model_dump(mode="json")
                },
                user_data.user_id,
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
        if websocket in self.active_connections.get(user_id, []):

            if len(self.active_connections[user_id]) > 1:
                self.active_connections[user_id].remove(websocket)
            else:
                self.active_connections.pop(user_id)
                await self._broadcast({"event": "user_disconnected", "user_id": user_id})

        return

    async def _broadcast(self, message: dict, exclude: int = None) -> None:
        """
        Send a message to all connected users, optionally skipping one user.

        Args:
            message (dict): The message payload to broadcast.
            exclude (Optional[int]): User ID to exclude from the broadcast, if any.

        Returns:
            None
        """
        for user_id, websockets in self.active_connections.items():
            if user_id == exclude:
                continue
            for websocket in websockets:
                await websocket.send_json(message)

    async def send_personal_message(self, message: dict, user_id: int) -> None:
        """
        Send a message to all active connections belonging to a single user.

        Args:
            message (dict): The message payload to send.
            user_id (int): The ID of the target user.

        Returns:
            None
        """
        websockets = self.active_connections[user_id]
        for websocket in websockets:
            await websocket.send_json(message)
