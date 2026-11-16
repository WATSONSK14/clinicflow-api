from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from.user import User
    from.appointment import Appointment


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialty : Mapped[str] = mapped_column(String(100), nullable=False)
    room_number : Mapped[str] = mapped_column(String(20), nullable=False)
    working_start: Mapped[str] = mapped_column(String(5), default="09:00")
    working_end : Mapped[str] = mapped_column(String(5), default="17:00")


    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="doctor", cascade="all, delete-orphan"
    )