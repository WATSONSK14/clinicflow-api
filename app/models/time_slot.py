from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import Appointment




class TimeSlot(Base):
    __tablename__ = "time_slots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time : Mapped[str] = mapped_column(String(5), nullable=False, unique=True)
    end_time : Mapped[str] = mapped_column(String(5), nullable=False)

    appointments : Mapped[list["Appointment"]] = relationship("Appointment", back_populates="slot")