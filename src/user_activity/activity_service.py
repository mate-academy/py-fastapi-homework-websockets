import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect, status

from user_activity.activity_repo import UserActivityRepository
from user_activity.ws_activity_manager import UserActivityWebSocketManager
from schemas import UpdateUserActivitySchema


class UserActivityService:
    def __init__(
            self,
            activity_repo: UserActivityRepository,
            ws_manager: UserActivityWebSocketManager,
            jwt_auth_manager,
    ):
        self.activity_repo = activity_repo
        self.ws_manager = ws_manager
        self.jwt_auth_manager = jwt_auth_manager

    async def process(self, websocket: WebSocket) -> None:
        await websocket.accept()
        user_id = None

        try:

            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            token = data.get("token")
            if not token:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            try:
                payload = self.jwt_auth_manager.decode_access_token(token)
                user_id = payload.get("user_id") or payload.get("sub")
                if not user_id:
                    raise ValueError("Missing user_id")
                user_id = int(user_id)
            except Exception:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            email = payload.get("email", "")

            now = datetime.now(timezone.utc)
            updated_data = UpdateUserActivitySchema(
                user_id=user_id,
                email=email,
                status="online",
                connected_at=now,
                disconnected_at=None,
            )
            user_activity_schema = await self.activity_repo.update_user_activity(updated_data)

            await self.ws_manager.connect(websocket, user_activity_schema)

            active_users = await self.activity_repo.get_all_active_users()
            snapshot_message = {
                "event": "online_users",
                "users": [u.model_dump(mode="json") for u in active_users],
            }
            await self.ws_manager.send_personal_message(snapshot_message, user_id)

            while True:
                await websocket.receive_json()

        except WebSocketDisconnect:
            pass
        finally:
            if user_id is not None:
                await self.ws_manager.disconnect(user_id, websocket)

                if user_id not in self.ws_manager.active_connections:
                    offline_time = datetime.now(timezone.utc)
                    offline_data = UpdateUserActivitySchema(
                        user_id=user_id,
                        status="offline",
                        disconnected_at=offline_time,
                    )
                    await self.activity_repo.update_user_activity(offline_data)
