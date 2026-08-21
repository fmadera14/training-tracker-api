from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.routine import Routine
from src.model.routine_day import RoutineDay
from src.model.routine_exercise import RoutineExercise
from src.model.exercise import Exercise
from src.schemas.routine_exercise import (
    RoutineExerciseCreate,
    RoutineExerciseUpdate,
    RoutineExerciseReorder,
    RoutineExerciseOut,
)

router = APIRouter(prefix="/routine-exercise", tags=["routine-exercise"])


def _get_owned_day(
    routine_day_id: UUID, current_user_id: str, db: Session
) -> RoutineDay:
    """Verifica que el día exista y pertenezca (vía rutina) al usuario actual."""
    day = (
        db.query(RoutineDay)
        .join(Routine)
        .filter(
            and_(
                RoutineDay.id == routine_day_id,
                Routine.user_id == current_user_id,
            )
        )
        .first()
    )
    if not day:
        raise HTTPException(status_code=404, detail="El día no existe")
    return day


@router.post(
    "/{routine_day_id}",
    response_model=RoutineExerciseOut,
    status_code=status.HTTP_201_CREATED,
)
def create_routine_exercise(
    routine_day_id: UUID,
    data: RoutineExerciseCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_day(routine_day_id, current_user_id, db)

    exercise = db.query(Exercise).filter(Exercise.id == data.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="El ejercicio no existe")

    new_routine_exercise = RoutineExercise(
        routine_day_id=routine_day_id,
        exercise_id=data.exercise_id,
        target_sets=data.target_sets,
        target_reps=data.target_reps,
        target_weight=data.target_weight,
        exercise_order=data.exercise_order,
        notes=data.notes,
    )
    db.add(new_routine_exercise)
    db.commit()
    db.refresh(new_routine_exercise)
    return new_routine_exercise


@router.patch("/{routine_exercise_id}", response_model=RoutineExerciseOut)
def edit_routine_exercise(
    routine_exercise_id: UUID,
    data: RoutineExerciseUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing = (
        db.query(RoutineExercise)
        .join(RoutineDay)
        .join(Routine)
        .filter(
            and_(
                RoutineExercise.id == routine_exercise_id,
                Routine.user_id == current_user_id,
            )
        )
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="El ejercicio de rutina no existe")

    update_data = data.model_dump(exclude_unset=True)

    if "exercise_id" in update_data:
        exercise = (
            db.query(Exercise).filter(Exercise.id == update_data["exercise_id"]).first()
        )
        if not exercise:
            raise HTTPException(status_code=404, detail="El ejercicio no existe")

    for field, value in update_data.items():
        setattr(existing, field, value)

    db.commit()
    db.refresh(existing)
    return existing


@router.patch("/{routine_day_id}/reorder", response_model=List[RoutineExerciseOut])
def reorder_routine_exercises(
    routine_day_id: UUID,
    reorder_data: RoutineExerciseReorder,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_day(routine_day_id, current_user_id, db)

    existing_exercises = (
        db.query(RoutineExercise)
        .filter(RoutineExercise.routine_day_id == routine_day_id)
        .all()
    )
    existing_ids = {re.id for re in existing_exercises}
    incoming_ids = set(reorder_data.routine_exercise_ids)

    if existing_ids != incoming_ids:
        raise HTTPException(
            status_code=400,
            detail="La lista debe incluir exactamente todos los ejercicios del día, sin repetidos ni faltantes",
        )

    exercises_by_id = {re.id: re for re in existing_exercises}

    for index, routine_exercise_id in enumerate(
        reorder_data.routine_exercise_ids, start=1
    ):
        exercises_by_id[routine_exercise_id].exercise_order = index

    db.commit()

    updated_exercises = (
        db.query(RoutineExercise)
        .filter(RoutineExercise.routine_day_id == routine_day_id)
        .order_by(RoutineExercise.exercise_order)
        .all()
    )
    return updated_exercises


@router.delete("/{routine_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_exercise(
    routine_exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing = (
        db.query(RoutineExercise)
        .join(RoutineDay)
        .join(Routine)
        .filter(
            and_(
                RoutineExercise.id == routine_exercise_id,
                Routine.user_id == current_user_id,
            )
        )
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="El ejercicio de rutina no existe")

    db.delete(existing)
    db.commit()
    return None
