from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class UserSettingCreate(BaseModel):
    weight_unit: str
    theme: str


class UserSettingUpdate(BaseModel):
    weight_unit: str | None = None
    theme: str | None = None


class UserSettingOut(BaseModel):
    id: UUID
    weight_unit: str
    theme: str
    created_at: datetime
    updated_at: datetime
    trainer_id: UUID | None = None

    class Config:
        from_attributes = True
