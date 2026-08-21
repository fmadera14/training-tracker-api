from decimal import Decimal
from pydantic import BaseModel
from uuid import UUID

from src.schemas.exercise import ExerciseOut


class RoutineExerciseCreate(BaseModel):
    exercise_id: UUID
    target_sets: int
    target_reps: int
    target_weight: Decimal
    exercise_order: int
    notes: str | None = None


class RoutineExerciseUpdate(BaseModel):
    exercise_id: UUID | None = None
    target_sets: int | None = None
    target_reps: int | None = None
    target_weight: Decimal | None = None
    exercise_order: int | None = None
    notes: str | None = None


class RoutineExerciseReorder(BaseModel):
    exercise_ids: list[UUID]


class RoutineExerciseOut(BaseModel):
    id: UUID
    routine_day_id: UUID
    target_sets: int
    target_reps: int
    target_weight: Decimal
    exercise_order: int
    notes: str | None = None
    exercise: ExerciseOut  # en vez de exercise_id

    class Config:
        from_attributes = True
