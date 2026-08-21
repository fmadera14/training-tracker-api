from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.workout_session import WorkoutSession
from src.model.workout_exercise import WorkoutExercise
from src.model.workout_set import WorkoutSet
from src.schemas.workout_set import (
    WorkoutSetCreate,
    WorkoutSetUpdate,
    WorkoutSetReorder,
    WorkoutSetOut,
)

router = APIRouter(prefix="/workout-set", tags=["workout-set"])


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


def _get_owned_set(set_id: UUID, current_user_id: str, db: Session) -> WorkoutSet:
    ws = (
        db.query(WorkoutSet)
        .join(WorkoutExercise)
        .join(WorkoutSession)
        .filter(
            and_(
                WorkoutSet.id == set_id,
                WorkoutSession.user_id == current_user_id,
            )
        )
        .first()
    )
    if not ws:
        raise HTTPException(status_code=404, detail="El set no existe")
    return ws


@router.post(
    "/{workout_exercise_id}",
    response_model=WorkoutSetOut,
    status_code=status.HTTP_201_CREATED,
)
def create_set(
    workout_exercise_id: UUID,
    data: WorkoutSetCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_workout_exercise(workout_exercise_id, current_user_id, db)

    new_set = WorkoutSet(
        workout_exercise_id=workout_exercise_id,
        set_number=data.set_number,
        reps=data.reps,
        weight=data.weight,
        completed=data.completed,
        notes=data.notes,
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set


@router.patch("/{set_id}", response_model=WorkoutSetOut)
def edit_set(
    set_id: UUID,
    data: WorkoutSetUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    ws = _get_owned_set(set_id, current_user_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ws, field, value)
    db.commit()
    db.refresh(ws)
    return ws


@router.patch("/{workout_exercise_id}/reorder", response_model=List[WorkoutSetOut])
def reorder_sets(
    workout_exercise_id: UUID,
    reorder_data: WorkoutSetReorder,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_workout_exercise(workout_exercise_id, current_user_id, db)

    existing = (
        db.query(WorkoutSet)
        .filter(WorkoutSet.workout_exercise_id == workout_exercise_id)
        .all()
    )
    existing_ids = {ws.id for ws in existing}
    incoming_ids = set(reorder_data.set_ids)

    if existing_ids != incoming_ids:
        raise HTTPException(
            status_code=400,
            detail="La lista debe incluir exactamente todos los sets del ejercicio",
        )

    by_id = {ws.id: ws for ws in existing}
    for index, ws_id in enumerate(reorder_data.set_ids, start=1):
        by_id[ws_id].set_number = index

    db.commit()

    return (
        db.query(WorkoutSet)
        .filter(WorkoutSet.workout_exercise_id == workout_exercise_id)
        .order_by(WorkoutSet.set_number)
        .all()
    )


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(
    set_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    ws = _get_owned_set(set_id, current_user_id, db)
    db.delete(ws)
    db.commit()
    return None
