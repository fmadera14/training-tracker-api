from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.config import get_current_user_id
from src.database import get_db
from src.model.routine import Routine
from src.model.routine_day import RoutineDay
from src.schemas.routine_days import (
    RoutineDayCreate,
    RoutineDayUpdate,
    RoutineDayReorder,
    RoutineDayOut,
)

router = APIRouter(prefix="/routine-day", tags=["routine-day"])


def _get_owned_routine(routine_id: UUID, current_user_id: str, db: Session) -> Routine:
    """Verifica que la rutina exista y pertenezca al usuario actual."""
    routine = (
        db.query(Routine)
        .filter(and_(Routine.id == routine_id, Routine.user_id == current_user_id))
        .first()
    )
    if not routine:
        raise HTTPException(status_code=404, detail="La rutina no existe")
    return routine


@router.post(
    "/{routine_id}", response_model=RoutineDayOut, status_code=status.HTTP_201_CREATED
)
def create_routine_day(
    routine_id: UUID,
    day_data: RoutineDayCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_routine(routine_id, current_user_id, db)

    existing_day = (
        db.query(RoutineDay)
        .filter(
            and_(
                RoutineDay.routine_id == routine_id,
                RoutineDay.day_order == day_data.day_order,
            )
        )
        .first()
    )
    if existing_day:
        raise HTTPException(
            status_code=400, detail="Ya existe un día con ese día order en esta rutina"
        )

    new_day = RoutineDay(
        routine_id=routine_id,
        name=day_data.name,
        day_order=day_data.day_order,
    )
    db.add(new_day)
    db.commit()
    db.refresh(new_day)
    return new_day


@router.patch("/{day_id}", response_model=RoutineDayOut)
def edit_routine_day(
    day_id: UUID,
    day_data: RoutineDayUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing_day = (
        db.query(RoutineDay)
        .join(Routine)
        .filter(and_(RoutineDay.id == day_id, Routine.user_id == current_user_id))
        .first()
    )
    if not existing_day:
        raise HTTPException(status_code=404, detail="El día no existe")

    update_data = day_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_day, field, value)

    db.commit()
    db.refresh(existing_day)
    return existing_day


@router.patch("/{routine_id}/reorder", response_model=List[RoutineDayOut])
def reorder_routine_days(
    routine_id: UUID,
    reorder_data: RoutineDayReorder,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    _get_owned_routine(routine_id, current_user_id, db)

    existing_days = (
        db.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).all()
    )
    existing_ids = {day.id for day in existing_days}
    incoming_ids = set(reorder_data.day_ids)

    if existing_ids != incoming_ids:
        raise HTTPException(
            status_code=400,
            detail="La lista debe incluir exactamente todos los días de la rutina, sin repetidos ni faltantes",
        )

    days_by_id = {day.id: day for day in existing_days}

    for index, day_id in enumerate(reorder_data.day_ids, start=1):
        days_by_id[day_id].day_order = index

    db.commit()

    updated_days = (
        db.query(RoutineDay)
        .filter(RoutineDay.routine_id == routine_id)
        .order_by(RoutineDay.day_order)
        .all()
    )
    return updated_days


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_day(
    day_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    existing_day = (
        db.query(RoutineDay)
        .join(Routine)
        .filter(and_(RoutineDay.id == day_id, Routine.user_id == current_user_id))
        .first()
    )
    if not existing_day:
        raise HTTPException(status_code=404, detail="El día no existe")

    db.delete(existing_day)
    db.commit()
    return None
