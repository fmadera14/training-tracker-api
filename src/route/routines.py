from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from typing import List

from uuid import UUID

from src.config import get_current_user_id
from src.database import get_db
from src.model.routine import Routine
from src.model.routine_day import RoutineDay
from src.model.routine_exercise import RoutineExercise
from src.schemas.routine import RoutineCreate, RoutineUpdate, RoutineOut

router = APIRouter(prefix="/routine", tags=["routine"])


@router.get("/", response_model=List[RoutineOut])
def my_routines(
    db: Session = Depends(get_db),
    current_user_id: Session = Depends(get_current_user_id),
):
    routines = db.query(Routine).filter(Routine.user_id == current_user_id).all()
    return routines


@router.post("/", response_model=RoutineOut, status_code=status.HTTP_201_CREATED)
def create_routine(
    routine_data: RoutineCreate,
    db: Session = Depends(get_db),
    current_user_id: Session = Depends(get_current_user_id),
):
    existing_routine = (
        db.query(Routine)
        .filter(
            and_(Routine.name == routine_data.name, Routine.user_id == current_user_id)
        )
        .first()
    )

    if existing_routine:
        raise HTTPException(status_code=400, detail="La rutina ya está registrada")

    new_routine = Routine(
        name=routine_data.name,
        description=routine_data.description,
        user_id=current_user_id,
    )
    db.add(new_routine)
    db.commit()
    db.refresh(new_routine)
    return new_routine


@router.post(
    "/duplicate/{routine_id}",
    response_model=RoutineOut,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_routine(
    routine_id: str,
    db: Session = Depends(get_db),
    current_user_id: Session = Depends(get_current_user_id),
):
    routine_to_duplicate = (
        db.query(Routine)
        .filter(and_(Routine.id == routine_id, Routine.user_id == current_user_id))
        .first()
    )

    duplicated_routine = Routine(
        name=routine_to_duplicate.name + "(Copy)",
        description=routine_to_duplicate.description,
        user_id=routine_to_duplicate.user_id,
    )
    db.add(duplicated_routine)
    db.commit()
    db.refresh(duplicated_routine)

    # create routine_days
    routine_days: list[RoutineDay] = routine_to_duplicate.days
    for day in routine_days:
        day_copy = RoutineDay(
            routine_id=duplicated_routine.id,
            name=day.name,
            day_order=day.day_order,
        )
        db.add(day_copy)
        db.commit()
        db.refresh(day_copy)

        # TODO: create routine_exercises
        routine_exercises: list[RoutineExercise] = day.exercises
        for exercise in routine_exercises:
            exercise_copy = RoutineExercise(
                routine_day_id=day_copy.id,
                exercise_id=exercise.exercise_id,
                target_sets=exercise.target_sets,
                target_reps=exercise.target_reps,
                target_weight=exercise.target_weight,
                exercise_order=exercise.exercise_order,
                notes=exercise.notes,
            )
            db.add(exercise_copy)
            db.commit()

    return duplicated_routine


@router.patch("/{routine_id}", response_model=RoutineOut)
def edit_routine(
    routine_id: UUID,
    routine_data: RoutineUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing_routine = (
        db.query(Routine)
        .filter(
            and_(
                Routine.id == routine_id,
                Routine.user_id == current_user_id,
            )
        )
        .first()
    )

    if not existing_routine:
        raise HTTPException(status_code=404, detail="La rutina no existe")

    update_data = routine_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate = (
            db.query(Routine)
            .filter(
                and_(
                    Routine.name == update_data["name"],
                    Routine.user_id == current_user_id,
                    Routine.id != routine_id,
                )
            )
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400, detail="Ya tienes otra rutina con ese nombre"
            )

    for field, value in update_data.items():
        setattr(existing_routine, field, value)

    db.commit()
    db.refresh(existing_routine)
    return existing_routine


@router.delete("/{routine_id}")
def delete_routine(
    routine_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: Session = Depends(get_current_user_id),
):
    existing_routine = (
        db.query(Routine)
        .filter(and_(Routine.id == routine_id, Routine.user_id == current_user_id))
        .first()
    )
    if not existing_routine:
        raise HTTPException(status_code=404, detail="La rutina no existe")

    db.delete(existing_routine)
    db.commit()
    return {"message": "Rutina eliminada exitosamente"}
