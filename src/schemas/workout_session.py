from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from src.schemas.workout_exercise import WorkoutExerciseOut


class WorkoutSessionCreate(BaseModel):
    routine_day_id: UUID | None = None
    name: str | None = None
    notes: str | None = None


class WorkoutSessionUpdate(BaseModel):
    notes: str | None = None


class WorkoutSessionOut(BaseModel):
    id: UUID
    user_id: UUID
    routine_day_id: UUID | None = None
    name: str
    started_at: datetime
    finished_at: datetime | None = None
    notes: str | None = None
    workout_exercises: list[WorkoutExerciseOut]

    class Config:
        from_attributes = True
