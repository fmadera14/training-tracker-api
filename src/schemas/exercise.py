from pydantic import BaseModel
from uuid import UUID


class ExerciseCreate(BaseModel):
    name: str
    mouscle_group: str
    user_id: UUID | None = None


class ExerciseUpdate(BaseModel):
    name: str
    mouscle_group: str
    user_id: UUID


class ExerciseOut(BaseModel):
    id: UUID
    name: str
    mouscle_group: str
    user_id: UUID | None = None

    class Config:
        from_attributes = True
