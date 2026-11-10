from abc import ABC, abstractmethod

from fastapi import WebSocket

from schemas.user_activity import (
    UpdateUserActivitySchema,
    UserActivitySchema,
    UserBaseDTO,
)


class UserActivityRepoInterface(ABC):
    """Abstract interface for persisting and querying user online activity."""

    @abstractmethod
    async def create_user_activity(self, user_data: UserBaseDTO) -> None:
        """
        Create the initial activity record for a user.

        Args:
            user_data (UserBaseDTO): Basic user data used to seed the record.

        Returns:
            None
        """

    @abstractmethod
    async def update_user_activity(self, user_data: UpdateUserActivitySchema) -> UserActivitySchema:
        """
        Update a user's activity status.

        Args:
            user_data (UpdateUserActivitySchema): Fields to update on the activity record.

        Returns:
            UserActivitySchema: The updated activity record.
        """

    @abstractmethod
    async def get_all_active_users(self) -> list[UserActivitySchema]:
        """
        Retrieve all currently online users.

        Returns:
            List[UserActivitySchema]: Activity records for all online users.
        """


class UserActivityWebSocketManagerInterface(ABC):
    """Abstract interface for managing active WebSocket connections and broadcasting activity events."""

    @abstractmethod
    async def connect(self, websocket: WebSocket, user_data: UserActivitySchema) -> None:
        """
        Register a new WebSocket connection for a user.

        Args:
            websocket (WebSocket): The WebSocket connection to register.
            user_data (UserActivitySchema): The connecting user's activity data.

        Returns:
            None
        """

    @abstractmethod
    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection for a user.

        Args:
            user_id (int): The ID of the disconnecting user.
            websocket (WebSocket): The WebSocket connection to remove.

        Returns:
            None
        """

    @abstractmethod
    async def _broadcast(
        self,
        message: dict,
        exclude: int | None = None,
    ) -> None:
        """
        Broadcast a message to all connected users, optionally excluding one user.

        Args:
            message (dict): The message payload to broadcast.
            exclude (Optional[int]): User ID to exclude from the broadcast, if any.

        Returns:
            None
        """

    @abstractmethod
    async def send_personal_message(self, message: dict, user_id: int) -> None:
        """
        Send a message to all active connections of a single user.

        Args:
            message (dict): The message payload to send.
            user_id (int): The ID of the user to send the message to.

        Returns:
            None
        """


class UserActivityServiceInterface(ABC):

    @abstractmethod
    async def process(self, websocket: WebSocket) -> None:
        """
        Handle a single WebSocket connection end-to-end (auth, tracking, cleanup).

        Args:
            websocket (WebSocket): The incoming WebSocket connection.

        Returns:
            None
        """
