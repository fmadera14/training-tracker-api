import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class RoutineExercise(Base):
    __tablename__ = "routine_exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    routine_day_id = Column(
        UUID(as_uuid=True), ForeignKey("routine_days.id"), nullable=False
    )
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    target_sets = Column(Integer, nullable=False)
    target_reps = Column(Integer, nullable=False)
    target_weight = Column(Float, nullable=False)
    exercise_order = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    day = relationship("RoutineDay", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="routine_exercises")
