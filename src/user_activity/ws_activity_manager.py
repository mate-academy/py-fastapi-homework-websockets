
from fastapi import WebSocket

from schemas.user_activity import UserActivitySchema
from user_activity.interfaces import UserActivityWebSocketManagerInterface


class UserActivityWebSocketManager(UserActivityWebSocketManagerInterface):
    """In-memory implementation of the WebSocket connection manager for user activity tracking."""

    def __init__(self) -> None:
        """Initialize an empty mapping of user IDs to their active WebSocket connections."""
        self.active_connections: dict[int, list[WebSocket]] = {}

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
        is_first_connection = user_data.user_id not in self.active_connections

        if is_first_connection:
            self.active_connections[user_data.user_id] = []

        self.active_connections[user_data.user_id].append(websocket)

        if is_first_connection:
            await self._broadcast(
                {
                    "event": "user_connected",
                    "user": user_data.model_dump(mode="json"),
                },
                exclude=user_data.user_id,
            )

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id)

        if not connections:
            return

        connections.remove(websocket)

        if not connections:
            del self.active_connections[user_id]

            await self._broadcast(
                {
                    "event": "user_disconnected",
                    "user_id": user_id,
                },
                exclude=user_id,
            )

    async def _broadcast(
        self,
        message: dict,
        exclude: int | None = None,
    ) -> None:
        """
        Send a message to all connected users, optionally skipping one user.

        Args:
            message (dict): The message payload to broadcast.
            exclude (Optional[int]): User ID to exclude from the broadcast, if any.

        Returns:
            None
        """
        for user_id, connections in self.active_connections.items():
            if user_id == exclude:
                continue

            for websocket in connections:
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
        connections = self.active_connections.get(user_id, [])

        for websocket in connections:
            await websocket.send_json(message)
