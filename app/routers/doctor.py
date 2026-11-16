from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.models.doctor import Doctor
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileResponse,
    DoctorDetailResponse,
    DoctorProfileUpdate,
)

from datetime import date
from app.models.time_slot import TimeSlot
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.schemas.appointment import TimeSlotResponse
from app.dependencies import require_roles

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN))]

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/profile", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_in : DoctorProfileCreate, current_user: CurrentUser , db: DbSession) -> Doctor:
    
    target_user_id = doctor_in.user_id if (current_user.role == UserRole.ADMIN and doctor_in.user_id) else current_user.id
    
    
    doctor = db.execute(select(Doctor).filter_by(user_id=target_user_id)).scalar_one_or_none()

    if doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profiliniz zaten mevcut"
        )

    

    new_doctor = Doctor(
        user_id=target_user_id,
        specialty=doctor_in.specialty,
        room_number=doctor_in.room_number,
        working_start=doctor_in.working_start,
        working_end=doctor_in.working_end,
)

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor



@router.get("/", response_model=list[DoctorDetailResponse])
def doctors(db: DbSession , specialty: str | None = None) -> Doctor:

    if specialty:
        doctors = db.execute(select(Doctor).options(joinedload(Doctor.user)).filter(Doctor.specialty == specialty)).scalars().all()
    else:
        doctors = db.execute(select(Doctor).options(joinedload(Doctor.user))).scalars().all()

    return doctors


@router.get("/{doctor_id}", response_model=DoctorDetailResponse)
def doctor(doctor_id : int, db:DbSession) -> Doctor:
    doctor = db.execute(select(Doctor).options(joinedload(Doctor.user)).filter_by(id=doctor_id)).scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Böyle Bir Doktor Mevcut Değil."
        )

    return doctor


@router.put("/{doctor_id}", response_model=DoctorProfileResponse)
def update_doctor(
    doctor_id: int,
    doctor_in: DoctorProfileUpdate,
    db: DbSession,
    current_user: CurrentUser
) -> Doctor:

    doctor = db.execute(select(Doctor).filter_by(id=doctor_id)).scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Böyle bir doktor mevcut değil."
        )

    if current_user.role != UserRole.ADMIN and current_user.id != doctor.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu profili güncelleme yetkiniz bulunmamaktadır."
        )

    for key, value in doctor_in.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id : int, db: DbSession, current_user: CurrentUser) -> None:
    doctor = db.execute(select(Doctor).filter_by(id=doctor_id)).scalar_one_or_none()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Böyle Bir Doktor Bulunamadı"
        )

    if current_user.role != UserRole.ADMIN and current_user.id != doctor.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu profili silme yetkiniz bulunmamaktadır."
        )

    db.delete(doctor)
    db.commit()

    return None


@router.get("/{doctor_id}/available-slots", response_model=list[TimeSlotResponse])
def get_available_slots(doctor_id : int, appointment_date : date, db: Annotated[Session, Depends(get_db)]):

    doctor = db.execute(select(Doctor).filter_by(id=doctor_id)).scalar_one_or_none()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Böyle bir doktor mevcut değil."
        )

    if appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçmiş bir tarihe ait randevu saatleri sorgulanamaz."
        )

    doctor_slots = db.execute(select(TimeSlot).filter(
        TimeSlot.start_time >= doctor.working_start,
        TimeSlot.end_time <= doctor.working_end,
    ).order_by(TimeSlot.start_time)).scalars().all()

    booked_slots_ids = set(db.execute(
        select(Appointment.slot_id).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
    ).scalars().all())

    result = []

    for slot in doctor_slots:
        result.append(TimeSlotResponse(
            id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            is_available=(slot.id not in booked_slots_ids)
        ))

    return result