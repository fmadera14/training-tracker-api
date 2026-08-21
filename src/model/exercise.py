import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"), nullable=True)
    name = Column(String, nullable=False)
    mouscle_group = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="exercises")
    routine_exercises = relationship(
        "RoutineExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workout_exercises = relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
