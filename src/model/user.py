import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "profile"  # debe ser EXACTAMENTE el nombre de tu tabla en Supabase

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    weight_unit = Column(String, nullable=False)
    theme = Column(String, nullable=False)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"), nullable=True)

    exercises = relationship("Exercise", back_populates="owner")
    routines = relationship("Routine", back_populates="owner")
    workout_sessions = relationship("WorkoutSession", back_populates="owner")

    trainer = relationship("User", remote_side="User.id", foreign_keys=[trainer_id])

    trainer_requests_sent = relationship(
        "TrainerRequest",
        back_populates="user",
        foreign_keys="TrainerRequest.user_id",
    )

    trainer_requests_received = relationship(
        "TrainerRequest",
        back_populates="trainer",
        foreign_keys="TrainerRequest.trainer_id",
    )
