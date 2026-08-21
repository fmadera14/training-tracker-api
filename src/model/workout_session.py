import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"), nullable=False)
    routine_day_id = Column(
        UUID(as_uuid=True), ForeignKey("routine_days.id"), nullable=True
    )
    name = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)

    owner = relationship("User", back_populates="workout_sessions")
    routine = relationship("RoutineDay", back_populates="workout_sessions")
    workout_exercises = relationship("WorkoutExercise", back_populates="session")
