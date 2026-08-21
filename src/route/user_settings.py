from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config import get_current_user_id
from src.database import get_db
from src.model import User
from src.schemas.user_settings import UserSettingUpdate, UserSettingOut

router = APIRouter(prefix="/user-settings", tags=["user-settings"])


@router.get("/", response_model=UserSettingOut)
def get_my_settings(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    settings = db.query(User).filter(User.id == current_user_id).first()
    if not settings:
        raise HTTPException(
            status_code=404, detail="Aún no has configurado tus ajustes"
        )
    return settings


@router.patch("/", response_model=UserSettingOut)
def update_my_settings(
    data: UserSettingUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    settings = db.query(User).filter(User.id == current_user_id).first()
    if not settings:
        raise HTTPException(
            status_code=404, detail="Aún no has configurado tus ajustes"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings
