from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.user import User
from src.model.trainer_request import TrainerRequest
from src.schemas.trainer_request import TrainerRequestCreate, TrainerRequestOut

router = APIRouter(prefix="/trainer-request", tags=["trainer-request"])


@router.get("/sent", response_model=List[TrainerRequestOut])
def my_sent_requests(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Requests que YO envié a entrenadores."""
    return (
        db.query(TrainerRequest)
        .filter(TrainerRequest.user_id == current_user_id)
        .order_by(TrainerRequest.created_at.desc())
        .all()
    )


@router.get("/received", response_model=List[TrainerRequestOut])
def my_received_requests(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Requests que recibí como entrenador."""
    return (
        db.query(TrainerRequest)
        .filter(TrainerRequest.trainer_id == current_user_id)
        .order_by(TrainerRequest.created_at.desc())
        .all()
    )


@router.post("/", response_model=TrainerRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    data: TrainerRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    current_profile = db.query(User).filter(User.id == current_user_id).first()

    if current_profile.trainer_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Ya tienes un entrenador asignado, debes desvincularte primero",
        )

    trainer = db.query(User).filter(User.email == data.trainer_email).first()
    if not trainer:
        raise HTTPException(
            status_code=404, detail="No existe un usuario con ese email"
        )

    if str(trainer.id) == str(current_user_id):
        raise HTTPException(
            status_code=400, detail="No puedes enviarte un request a ti mismo"
        )

    existing_pending = (
        db.query(TrainerRequest)
        .filter(
            and_(
                TrainerRequest.user_id == current_user_id,
                TrainerRequest.trainer_id == trainer.id,
                TrainerRequest.status == "pending",
            )
        )
        .first()
    )
    if existing_pending:
        raise HTTPException(
            status_code=400, detail="Ya tienes un request pendiente con este entrenador"
        )

    new_request = TrainerRequest(
        user_id=current_user_id,
        trainer_id=trainer.id,
        status="pending",
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


@router.patch("/{request_id}/accept", response_model=TrainerRequestOut)
def accept_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    request = (
        db.query(TrainerRequest)
        .filter(
            and_(
                TrainerRequest.id == request_id,
                TrainerRequest.trainer_id == current_user_id,
            )
        )
        .first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="El request no existe")

    if request.status != "pending":
        raise HTTPException(
            status_code=400, detail="Este request ya fue procesado anteriormente"
        )

    request.status = "accepted"

    user_profile = db.query(User).filter(User.id == request.user_id).first()
    user_profile.trainer_id = request.trainer_id

    other_pending = (
        db.query(TrainerRequest)
        .filter(
            and_(
                TrainerRequest.user_id == request.user_id,
                TrainerRequest.status == "pending",
                TrainerRequest.id != request.id,
            )
        )
        .all()
    )
    for other in other_pending:
        other.status = "declined"

    db.commit()
    db.refresh(request)
    return request


@router.patch("/{request_id}/decline", response_model=TrainerRequestOut)
def decline_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    request = (
        db.query(TrainerRequest)
        .filter(
            and_(
                TrainerRequest.id == request_id,
                TrainerRequest.trainer_id == current_user_id,
            )
        )
        .first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="El request no existe")

    if request.status != "pending":
        raise HTTPException(
            status_code=400, detail="Este request ya fue procesado anteriormente"
        )

    request.status = "declined"
    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    request = (
        db.query(TrainerRequest)
        .filter(
            and_(
                TrainerRequest.id == request_id,
                TrainerRequest.user_id == current_user_id,
            )
        )
        .first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="El request no existe")

    if request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Solo puedes eliminar requests que aún están pendientes",
        )

    db.delete(request)
    db.commit()
    return None
