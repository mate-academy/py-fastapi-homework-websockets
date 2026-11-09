import asyncio
from datetime import datetime, timezone
from typing import Optional

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

    AUTH_TIMEOUT_SECONDS = 30

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

        user_id = await self._authenticate(websocket)
        if user_id is None:
            return

        user_data = await self.activity_repo.update_user_activity(
            UpdateUserActivitySchema(
                user_id=user_id,
                status="online",
                connected_at=datetime.now(timezone.utc),
            )
        )

        await self.activity_ws_manager.connect(websocket, user_data)

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
        except WebSocketDisconnect:
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

    async def _authenticate(self, websocket: WebSocket) -> Optional[int]:
        """
        Read the first message from the client and resolve the user ID from its token.

        Closes the connection with WS_1008_POLICY_VIOLATION if no message arrives
        in time, the message has no token, or the token is invalid/expired.

        Args:
            websocket (WebSocket): The accepted WebSocket connection.

        Returns:
            Optional[int]: The authenticated user's ID, or None if authentication failed.
        """
        try:
            auth_message = await asyncio.wait_for(
                websocket.receive_json(), timeout=self.AUTH_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        except WebSocketDisconnect:
            return None
        except ValueError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        token = auth_message.get("token") if isinstance(auth_message, dict) else None
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        try:
            payload = self.jwt_auth_manager.decode_access_token(token)
        except (TokenExpiredError, InvalidTokenError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        user_id = payload.get("user_id")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        return user_id
