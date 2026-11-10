import asyncio
from datetime import UTC, datetime

from fastapi import WebSocket, WebSocketDisconnect, status

from exceptions import InvalidTokenError, TokenExpiredError
from schemas.user_activity import UpdateUserActivitySchema
from security.interfaces import JWTAuthManagerInterface
from user_activity.interfaces import (
    UserActivityRepoInterface,
    UserActivityServiceInterface,
    UserActivityWebSocketManagerInterface,
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
            token_data = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=30,
            )
        except TimeoutError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = token_data.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            payload = self.jwt_auth_manager.decode_access_token(token)
        except (TokenExpiredError, InvalidTokenError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_data = await self.activity_repo.update_user_activity(
            UpdateUserActivitySchema(
                user_id=user_id,
                status="online",
                connected_at=datetime.now(UTC),
            )
        )

        await self.activity_ws_manager.connect(websocket, user_data)

        active_users = await self.activity_repo.get_all_active_users()

        await self.activity_ws_manager.send_personal_message(
            {
                "event": "online_users",
                "users": [user.model_dump(mode="json") for user in active_users],
            },
            user_id,
        )
        try:
            while True:
                await websocket.receive_json()
        except WebSocketDisconnect:
            pass
        finally:
            await self.activity_ws_manager.disconnect(user_id, websocket)

            if not self.activity_ws_manager.active_connections.get(user_id):
                await self.activity_repo.update_user_activity(
                    UpdateUserActivitySchema(
                        user_id=user_id,
                        status="offline",
                        disconnected_at=datetime.now(UTC),
                    )
                )
