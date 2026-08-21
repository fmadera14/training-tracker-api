from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config import get_current_user_id
from src.database import get_db
from src.model.user import User
from src.schemas.user import UserOut  # ajusta si tu schema se llama distinto

router = APIRouter(prefix="/profile", tags=["profile"])


@router.delete("/trainer", response_model=UserOut)
def remove_trainer(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    profile = db.query(User).filter(User.id == current_user_id).first()

    if profile.trainer_id is None:
        raise HTTPException(status_code=400, detail="No tienes un entrenador asignado")

    profile.trainer_id = None
    db.commit()
    db.refresh(profile)
    return profile
