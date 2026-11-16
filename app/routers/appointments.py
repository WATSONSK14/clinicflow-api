from datetime import date, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.enums import UserRole, AppointmentStatus
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.time_slot import TimeSlot
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentDetailResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_in: AppointmentCreate,
    current_user: CurrentUser,
    db: DbSession
) -> Appointment:

    if appointment_in.appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçmiş bir tarihe randevu alınamaz."
        )

    # PostgreSQL için hasta satırını kilitle
    db.execute(
        select(User)
        .filter(User.id == current_user.id)
        .with_for_update()
    ).scalar_one()

    doctor = db.execute(select(Doctor).filter_by(id=appointment_in.doctor_id)).scalar_one_or_none()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seçilen doktor bulunamadı."
        )
    
    user_appointments = db.execute(
    select(Appointment)
    .options(joinedload(Appointment.doctor))
    .filter_by(patient_id=current_user.id, status=AppointmentStatus.SCHEDULED)
).scalars().all()
    active_appointments = [appointment.doctor.specialty for appointment in user_appointments]


    if doctor.specialty in active_appointments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aynı Branştan Aynı Anda 1 Randevu Alabilirsiniz."
        )

    if len(active_appointments) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bir Kullanıcı Aynı Anda Sadece 3 Randevu Alabilir."
        )


    for appointment in user_appointments:
        if (
            appointment.slot_id == appointment_in.slot_id
            and appointment.appointment_date == appointment_in.appointment_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu Tarih ve Saatte Zaten Bir Randevunuz Var."
            )


    slot = db.execute(select(TimeSlot).filter_by(id=appointment_in.slot_id)).scalar_one_or_none()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geçersiz randevu saati dilimi."
        )

    if slot.start_time < doctor.working_start or slot.end_time > doctor.working_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Randevu saati doktorun çalışma saatleri ({doctor.working_start} - {doctor.working_end}) içinde olmalıdır."
        )

    existing_appointment = db.execute(
        select(Appointment).filter_by(
            doctor_id=appointment_in.doctor_id,
            appointment_date=appointment_in.appointment_date,
            slot_id=appointment_in.slot_id,
        )
    ).scalar_one_or_none()

    try:
        if existing_appointment:
            if existing_appointment.status != AppointmentStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Bu randevu saati doludur, lütfen başka bir saat seçiniz."
                )

            existing_appointment.patient_id = current_user.id
            existing_appointment.status = AppointmentStatus.SCHEDULED
            existing_appointment.notes = appointment_in.notes
            existing_appointment.created_at = datetime.utcnow()

            db.commit()
            db.refresh(existing_appointment)
            return existing_appointment

        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=appointment_in.doctor_id,
            slot_id=appointment_in.slot_id,
            appointment_date=appointment_in.appointment_date,
            notes=appointment_in.notes,
        )

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu randevu saati başka bir kullanıcı tarafından alındı."
        )
    



@router.get("/", response_model=list[AppointmentDetailResponse])
def get_appointments(current_user: CurrentUser, db: DbSession):

    query = select(Appointment).options(
        joinedload(Appointment.slot),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
        joinedload(Appointment.patient)
    )

    if current_user.role == UserRole.PATIENT:
        query = query.filter(Appointment.patient_id == current_user.id)
    
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.execute(select(Doctor).filter_by(user_id=current_user.id)).scalar_one_or_none()
        if not doctor:
            return []
        query = query.filter(Appointment.doctor_id == doctor.id)


    appointments = db.execute(query).scalars().all()
    return appointments


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int, current_user: CurrentUser, db: DbSession) -> Appointment:

    appointment = db.execute(select(Appointment).filter_by(id=appointment_id).with_for_update()).scalar_one_or_none()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Randevu bulunamadı!",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu randevu iptal edilemez."
        )

    if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu randevuyu iptal etme yetkiniz yok!")

    if current_user.role == UserRole.DOCTOR:
        doctor = db.execute(select(Doctor).filter_by(user_id=current_user.id)).scalar_one_or_none()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu randevuyu iptal etme yetkiniz yok!")

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu randevu zaten iptal edilmiş.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)

    return appointment

