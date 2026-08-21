from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


class TrainerRequestCreate(BaseModel):
    trainer_email: EmailStr


class TrainerRequestOut(BaseModel):
    id: UUID
    user_id: UUID
    trainer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
