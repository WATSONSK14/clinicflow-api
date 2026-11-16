import html
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime
from app.models.enums import AppointmentStatus
from app.schemas.user import UserResponse
from app.schemas.doctor import DoctorDetailResponse


class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: date
    slot_id: int
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, v: str | None) -> str | None:
        if v:
            return html.escape(v.strip())
        return v


class TimeSlotResponse(BaseModel):
    id: int
    start_time: str
    end_time: str
    is_available: bool = True
    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    start_time: str
    end_time: str
    status: AppointmentStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AppointmentDetailResponse(AppointmentResponse):
    patient: UserResponse | None = None
    doctor: DoctorDetailResponse | None = None
