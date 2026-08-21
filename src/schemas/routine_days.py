from pydantic import BaseModel
from uuid import UUID
from src.schemas.routine_exercise import RoutineExerciseOut


class RoutineDayCreate(BaseModel):
    name: str
    day_order: int


class RoutineDayUpdate(BaseModel):
    name: str | None = None
    day_order: int | None = None


class RoutineDayReorder(BaseModel):
    day_ids: list[UUID]


class RoutineDayOut(BaseModel):
    id: UUID
    routine_id: UUID
    name: str
    day_order: int
    exercises: list[RoutineExerciseOut] = []

    class Config:
        from_attributes = True
