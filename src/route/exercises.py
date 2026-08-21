from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from typing import List

from uuid import UUID

from src.config import get_current_user_id
from src.database import get_db
from src.model.exercise import Exercise
from src.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseOut

router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("/", response_model=List[ExerciseOut])
def get_all(
    db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)
):
    exercises = (
        db.query(Exercise)
        .filter(
            or_(
                Exercise.user_id.is_(None),
                Exercise.user_id == current_user_id,
            )
        )
        .all()
    )
    return exercises


@router.post("/add", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
def add(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    existing_exercise = (
        db.query(Exercise)
        .filter(
            and_(
                Exercise.name == exercise_data.name,
                Exercise.user_id == exercise_data.user_id,
            )
        )
        .first()
    )
    if existing_exercise:
        raise HTTPException(status_code=400, detail="El ejercicio ya está registrado")

    new_exercise = Exercise(
        name=exercise_data.name,
        mouscle_group=exercise_data.mouscle_group,
        user_id=exercise_data.user_id,
    )

    try:
        db.add(new_exercise)
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="El user_id no existe en la base de datos"
        )
    db.refresh(new_exercise)
    return new_exercise


@router.post(
    "/add-multiple",
    response_model=List[ExerciseOut],
    status_code=status.HTTP_201_CREATED,
)
def add_multiple(
    exercises_data: List[ExerciseCreate],
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    if current_user_id != "8577d8de-fabb-45e9-abb2-754fc18ef928":
        raise HTTPException(
            status_code=403, detail="No tienes permiso para este endpoint"
        )

    new_exercises = [
        Exercise(
            name=item.name,
            mouscle_group=item.mouscle_group,
            user_id=item.user_id,
        )
        for item in exercises_data
    ]

    try:
        db.add_all(new_exercises)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Uno o más user_id no existen en la base de datos"
        )

    for exercise in new_exercises:
        db.refresh(exercise)

    return new_exercises


@router.put(
    "/{exercise_id}", response_model=ExerciseOut, status_code=status.HTTP_200_OK
)
def update_exercise(
    exercise_id: UUID,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing_exercise = (
        db.query(Exercise)
        .filter(
            and_(
                Exercise.id == exercise_id,
                Exercise.user_id == current_user_id,
            )
        )
        .first()
    )
    if not existing_exercise:
        raise HTTPException(status_code=404, detail="El ejercicio no existe")

    existing_exercise.name = exercise_data.name
    existing_exercise.mouscle_group = exercise_data.mouscle_group
    db.commit()
    db.refresh(existing_exercise)
    return existing_exercise


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing_exercise = (
        db.query(Exercise)
        .filter(and_(Exercise.id == exercise_id, Exercise.user_id == current_user_id))
        .first()
    )

    if not existing_exercise:
        raise HTTPException(status_code=404, detail="El ejercicio no existe")

    db.delete(existing_exercise)
    db.commit()
    return {"message": "Ejercicio eliminado correctamente"}
