from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.workout_session import WorkoutSession
from src.model.workout_exercise import WorkoutExercise
from src.model.exercise import Exercise
from src.schemas.workout_exercise import (
    WorkoutExerciseCreate,
    WorkoutExerciseUpdate,
    WorkoutExerciseReorder,
    WorkoutExerciseOut,
)

router = APIRouter(prefix="/workout-exercise", tags=["workout-exercise"])


def _get_owned_session(
    session_id: UUID, current_user_id: str, db: Session
) -> WorkoutSession:
    session = (
        db.query(WorkoutSession)
        .filter(
            and_(
                WorkoutSession.id == session_id,
                WorkoutSession.user_id == current_user_id,
            )
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="La sesión no existe")
    return session


def _get_owned_workout_exercise(
    workout_exercise_id: UUID, current_user_id: str, db: Session
) -> WorkoutExercise:
    we = (
        db.query(WorkoutExercise)
        .join(WorkoutSession)
        .filter(
            and_(
                WorkoutExercise.id == workout_exercise_id,
                WorkoutSession.user_id == current_user_id,
            )
        )
        .first()
    )
    if not we:
        raise HTTPException(
            status_code=404, detail="El ejercicio de la sesión no existe"
        )
    return we


@router.post(
    "/{session_id}",
    response_model=WorkoutExerciseOut,
    status_code=status.HTTP_201_CREATED,
)
def create_workout_exercise(
    session_id: UUID,
    data: WorkoutExerciseCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_session(session_id, current_user_id, db)

    exercise = db.query(Exercise).filter(Exercise.id == data.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="El ejercicio no existe")

    new_we = WorkoutExercise(
        session_id=session_id,
        exercise_id=data.exercise_id,
        exercise_number=data.exercise_number,
    )
    db.add(new_we)
    db.commit()
    db.refresh(new_we)
    return new_we


@router.patch("/{workout_exercise_id}", response_model=WorkoutExerciseOut)
def edit_workout_exercise(
    workout_exercise_id: UUID,
    data: WorkoutExerciseUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    we = _get_owned_workout_exercise(workout_exercise_id, current_user_id, db)

    update_data = data.model_dump(exclude_unset=True)
    if "exercise_id" in update_data:
        exercise = (
            db.query(Exercise).filter(Exercise.id == update_data["exercise_id"]).first()
        )
        if not exercise:
            raise HTTPException(status_code=404, detail="El ejercicio no existe")

    for field, value in update_data.items():
        setattr(we, field, value)

    db.commit()
    db.refresh(we)
    return we


@router.patch("/{session_id}/reorder", response_model=List[WorkoutExerciseOut])
def reorder_workout_exercises(
    session_id: UUID,
    reorder_data: WorkoutExerciseReorder,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_session(session_id, current_user_id, db)

    existing = (
        db.query(WorkoutExercise).filter(WorkoutExercise.session_id == session_id).all()
    )
    existing_ids = {we.id for we in existing}
    incoming_ids = set(reorder_data.exercise_ids)

    if existing_ids != incoming_ids:
        raise HTTPException(
            status_code=400,
            detail="La lista debe incluir exactamente todos los ejercicios de la sesión",
        )

    by_id = {we.id: we for we in existing}
    for index, we_id in enumerate(reorder_data.exercise_ids, start=1):
        by_id[we_id].exercise_number = index

    db.commit()

    return (
        db.query(WorkoutExercise)
        .filter(WorkoutExercise.session_id == session_id)
        .order_by(WorkoutExercise.exercise_number)
        .all()
    )


@router.delete("/{workout_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_exercise(
    workout_exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    we = _get_owned_workout_exercise(workout_exercise_id, current_user_id, db)
    db.delete(we)
    db.commit()
    return None
