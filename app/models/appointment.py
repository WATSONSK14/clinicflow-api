from datetime import date, datetime
from sqlalchemy import (
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AppointmentStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from.user import User
    from.doctor import Doctor
    from.time_slot import TimeSlot

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    slot_id : Mapped[int] = mapped_column(Integer, ForeignKey("time_slots.id"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date,nullable=False, index=True)
    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    patient: Mapped["User"] = relationship("User", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    slot: Mapped["TimeSlot"] = relationship("TimeSlot", back_populates="appointments")


    @property
    def start_time(self) -> str:
        return self.slot.start_time
    @property
    def end_time(self) -> str:
        return self.slot.end_time
    
    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "slot_id",
            name="uq_doctor_appointment_slot",
        ),
    )