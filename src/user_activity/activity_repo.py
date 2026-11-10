from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas import (
    UserBaseDTO,
    UpdateUserActivitySchema,
    UserActivitySchema,
)


class UserActivityRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.user_activity

    async def create_user_activity(self, user_data: UserBaseDTO) -> None:
        # Виправляємо user_data.user_id на user_data.id відповідно до UserBaseDTO
        await self.collection.update_one(
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
        update_dict = user_data.model_dump(exclude_unset=True)
        user_id = update_dict.pop("user_id")

        if update_dict:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": update_dict},
            )

        doc = await self.collection.find_one({"user_id": user_id}, {"_id": 0})
        return UserActivitySchema(**doc)

    async def get_all_active_users(self) -> List[UserActivitySchema]:
        cursor = self.collection.find({"status": "online"}, {"_id": 0})
        docs = await cursor.to_list(length=None)
        return [UserActivitySchema(**doc) for doc in docs]
