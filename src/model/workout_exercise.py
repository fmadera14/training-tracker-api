import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id"), nullable=False
    )
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    exercise_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("WorkoutSession", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    workout_sets = relationship("WorkoutSet", back_populates="workout_exercise")
