from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.routine_day import RoutineDay
from src.model.routine_exercise import RoutineExercise
from src.model.workout_session import WorkoutSession
from src.model.workout_exercise import WorkoutExercise
from src.model.workout_set import WorkoutSet
from src.schemas.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSessionOut,
)

router = APIRouter(prefix="/workout-session", tags=["workout-session"])


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


@router.get("/", response_model=List[WorkoutSessionOut])
def my_sessions(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    return (
        db.query(WorkoutSession)
        .filter(WorkoutSession.user_id == current_user_id)
        .order_by(WorkoutSession.started_at.desc())
        .all()
    )


@router.get("/{session_id}", response_model=WorkoutSessionOut)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    return _get_owned_session(session_id, current_user_id, db)


@router.post("/", response_model=WorkoutSessionOut, status_code=status.HTTP_201_CREATED)
def start_session(
    data: WorkoutSessionCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    routine = db.query(RoutineDay).filter(RoutineDay.id == data.routine_day_id).first()

    new_session = WorkoutSession(
        user_id=current_user_id,
        routine_day_id=data.routine_day_id,
        name=(
            f"{routine.routine.name} - {routine.name}"
            if routine is not None
            else data.name or "Quick Workout"
        ),
        notes=data.notes,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    if routine is not None:
        routine_exercises: list[RoutineExercise] = routine.exercises
        for exercise in routine_exercises:
            new_exercise = WorkoutExercise(
                session_id=new_session.id,
                exercise_id=exercise.exercise_id,
                exercise_number=exercise.exercise_order,
            )
            db.add(new_exercise)
            db.commit()
            db.refresh(new_exercise)

            for i in range(exercise.target_sets):
                new_set = WorkoutSet(
                    workout_exercise_id=new_exercise.id,
                    set_number=i + 1,
                    reps=exercise.target_reps,
                    weight=exercise.target_weight,
                    completed=False,
                )
                db.add(new_set)
                db.commit()
                db.refresh(new_set)

    return new_session


@router.patch("/{session_id}", response_model=WorkoutSessionOut)
def edit_session(
    session_id: UUID,
    data: WorkoutSessionUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session = _get_owned_session(session_id, current_user_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/{session_id}/finish", response_model=WorkoutSessionOut)
def finish_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session = _get_owned_session(session_id, current_user_id, db)
    if session.finished_at is not None:
        raise HTTPException(status_code=400, detail="La sesión ya está finalizada")
    session.finished_at = func.now()
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session = _get_owned_session(session_id, current_user_id, db)
    db.delete(session)
    db.commit()
    return None
