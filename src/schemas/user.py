from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class UserCreate(BaseModel):
    weight_unit: str
    theme: str


class UserUpdate(BaseModel):
    weight_unit: str | None = None
    theme: str | None = None


class UserOut(BaseModel):
    id: UUID
    display_name: str
    avatar_url: str | None = None
    email: str
    created_at: datetime
    updated_at: datetime
    trainer_id: UUID | None = None

    class Config:
        from_attributes = True
