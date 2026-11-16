from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from.doctor import Doctor
    from.appointment import Appointment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    doctor_profile: Mapped["Doctor"] = relationship(
        "Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )

