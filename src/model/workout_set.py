import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_exercise_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_exercises.id"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    completed = Column(Boolean, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workout_exercise = relationship("WorkoutExercise", back_populates="workout_sets")
