from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from src.schemas.routine_days import RoutineDayOut


class RoutineCreate(BaseModel):
    name: str
    description: str | None = None


class RoutineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoutineOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    days: list[RoutineDayOut] = []

    class Config:
        from_attributes = True
