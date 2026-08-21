import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database import Base


class TrainerRequest(Base):
    __tablename__ = "trainer_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"), nullable=False)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"), nullable=False)
    status = Column(
        String, nullable=False, default="pending"
    )  # pending | accepted | declined
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship(
        "User", back_populates="trainer_requests_sent", foreign_keys=[user_id]
    )
    trainer = relationship(
        "User", back_populates="trainer_requests_received", foreign_keys=[trainer_id]
    )
