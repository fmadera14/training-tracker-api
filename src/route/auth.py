from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from src.config import create_access_token, hash_password, verify_password
from src.database import get_db
from src.model import User
from src.schemas.auth import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    new_user = User(
        email=user_data.email,
        display_name=user_data.display_name or user_data.email,
        hashed_password=hash_password(user_data.password),
        weight_unit="lb",
        theme="System",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": str(new_user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}
