from typing import List

from pymongo.asynchronous.database import AsyncDatabase

from schemas.user_activity import (
    UserBaseDTO,
    UpdateUserActivitySchema,
    UserActivitySchema,
)
from user_activity.interfaces import UserActivityRepoInterface


class UserActivityRepository(UserActivityRepoInterface):
    """MongoDB-backend implementation of the user activity repository."""

    def __init__(self, db: AsyncDatabase) -> None:
        """
        Initialize the repository with a MongoDB database instance.

        Args:
            db (AsyncDatabase): The Motor async MongoDB database instance.
        """
        self.db = db

    async def create_user_activity(self, user_data: UserBaseDTO) -> None:
        """
        Create or reset a user's activity record with an initial "offline" status.

        Args:
            user_data (UserBaseDTO): Basic user data (id and email) to seed the activity record.

        Returns:
            None
        """
        await self.db["user_activity"].update_one(
            {"user_id": user_data.id},
            {
                "$set": {
                    "user_id": user_data.id,
                    "email": user_data.email,
                    "status": "offline",
                }
            },
            upsert=True,
        )

    async def update_user_activity(
        self, user_data: UpdateUserActivitySchema
    ) -> UserActivitySchema:
        """
        Update (or create) a user's activity record and return the resulting document.

        Args:
            user_data (UpdateUserActivitySchema): Fields to update on the user's activity record.

        Returns:
            UserActivitySchema: The updated activity record.
        """
        fields = {"status": user_data.status}
        if user_data.connected_at is not None:
            fields["connected_at"] = user_data.connected_at
        if user_data.disconnected_at is not None:
            fields["disconnected_at"] = user_data.disconnected_at

        await self.db["user_activity"].update_one(
            {"user_id": user_data.user_id},
            {"$set": fields},
            upsert=True,
        )

        document = await self.db["user_activity"].find_one(
            {"user_id": user_data.user_id},
            {"_id": 0},
        )
        return UserActivitySchema(**document)

    async def get_all_active_users(self) -> List[UserActivitySchema]:
        """
        Retrieve all users that currently have an "online" status.

        Returns:
            List[UserActivitySchema]: A list of activity records for all online users.
        """
        cursor = self.db["user_activity"].find({"status": "online"}, {"_id": 0})
        return [UserActivitySchema(**document) async for document in cursor]
