import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class RoutineDay(Base):
    __tablename__ = "routine_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    routine_id = Column(UUID(as_uuid=True), ForeignKey("routines.id"), nullable=False)
    name = Column(String, nullable=False)
    day_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    routine = relationship("Routine", back_populates="days")
    exercises = relationship(
        "RoutineExercise",
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="RoutineExercise.exercise_order",
    )
    workout_sessions = relationship("WorkoutSession", back_populates="routine")
