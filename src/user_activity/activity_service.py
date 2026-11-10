import asyncio
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect, status

from schemas.user_activity import UpdateUserActivitySchema
from security.interfaces import JWTAuthManagerInterface
from exceptions import TokenExpiredError, InvalidTokenError
from user_activity.interfaces import (
    UserActivityServiceInterface,
    UserActivityWebSocketManagerInterface,
    UserActivityRepoInterface
)


class UserActivityService(UserActivityServiceInterface):
    """Coordinates authentication and lifecycle handling for user activity WebSocket connections."""

    def __init__(
            self,
            manager: UserActivityWebSocketManagerInterface,
            activity_repo: UserActivityRepoInterface,
            jwt_auth_manager: JWTAuthManagerInterface
    ) -> None:
        """
        Initialize the service with its collaborating components.

        Args:
            manager (UserActivityWebSocketManagerInterface): Manager responsible for tracking
                active WebSocket connections and broadcasting events.
            activity_repo (UserActivityRepoInterface): Repository used to persist user activity state.
            jwt_auth_manager (JWTAuthManagerInterface): Manager used to decode and validate access tokens.
        """
        self.activity_ws_manager = manager
        self.activity_repo = activity_repo
        self.jwt_auth_manager = jwt_auth_manager

    async def process(self, websocket: WebSocket) -> None:
        """
        Handle the full lifecycle of a single user activity WebSocket connection.

        Accepts the connection, authenticates the user via a token sent as the
        first message, registers the connection, broadcasts online status,
        and cleans up (marking the user offline) once the connection closes.

        Args:
            websocket (WebSocket): The incoming WebSocket connection.

        Returns:
            None
        """
        await websocket.accept()

        try:
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=30)
        except WebSocketDisconnect:
            return
        except (asyncio.TimeoutError, ValueError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = auth_message.get("token") if isinstance(auth_message, dict) else None
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            payload = self.jwt_auth_manager.decode_access_token(token)
        except (TokenExpiredError, InvalidTokenError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = payload.get("user_id")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_activity = await self.activity_repo.update_user_activity(
            UpdateUserActivitySchema(
                user_id=user_id,
                status="online",
                connected_at=datetime.now(timezone.utc),
            )
        )
        await self.activity_ws_manager.connect(websocket, user_activity)

        try:
            active_users = await self.activity_repo.get_all_active_users()
            await self.activity_ws_manager.send_personal_message(
                {
                    "event": "online_users",
                    "users": [user.model_dump(mode="json") for user in active_users],
                },
                user_id,
            )
            while True:
                await websocket.receive_json()
        except (WebSocketDisconnect, ValueError):
            pass
        finally:
            await self.activity_ws_manager.disconnect(user_id, websocket)
            await self.activity_repo.update_user_activity(
                UpdateUserActivitySchema(
                    user_id=user_id,
                    status="offline",
                    disconnected_at=datetime.now(timezone.utc),
                )
            )
