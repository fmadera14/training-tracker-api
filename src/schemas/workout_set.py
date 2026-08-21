from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class WorkoutSetCreate(BaseModel):
    set_number: int
    reps: int
    weight: float
    completed: bool
    notes: str | None = None


class WorkoutSetUpdate(BaseModel):
    set_number: int | None = None
    reps: int | None = None
    weight: float | None = None
    completed: bool | None = None
    notes: str | None = None


class WorkoutSetReorder(BaseModel):
    set_ids: list[UUID]


class WorkoutSetOut(BaseModel):
    id: UUID
    set_number: int
    reps: int | None = None
    weight: float | None = None
    completed: bool
    notes: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
