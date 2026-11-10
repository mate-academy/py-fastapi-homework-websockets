from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseDTO(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UpdateUserActivitySchema(BaseModel):
    user_id: int
    status: str
    connected_at: datetime | None = None
    disconnected_at: datetime | None = None


class UserActivitySchema(UpdateUserActivitySchema):
    email: EmailStr
