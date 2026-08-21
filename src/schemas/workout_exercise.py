from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from src.schemas.exercise import ExerciseOut
from src.schemas.workout_set import WorkoutSetOut


class WorkoutExerciseCreate(BaseModel):
    exercise_id: UUID
    exercise_number: int


class WorkoutExerciseUpdate(BaseModel):
    exercise_id: UUID | None = None
    exercise_number: int | None = None


class WorkoutExerciseReorder(BaseModel):
    exercise_ids: list[UUID]


class WorkoutExerciseOut(BaseModel):
    id: UUID
    session_id: UUID
    exercise_number: int
    created_at: datetime
    exercise: ExerciseOut
    workout_sets: list[WorkoutSetOut]

    class Config:
        from_attributes = True
