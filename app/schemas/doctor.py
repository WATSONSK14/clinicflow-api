from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse

class DoctorProfileBase(BaseModel):
    specialty: str
    room_number: str
    working_start : str = "09:00"
    working_end : str = "17:00"


class DoctorProfileCreate(DoctorProfileBase):
    user_id: int | None = None


class DoctorProfileUpdate(BaseModel):
    specialty: str | None = None
    room_number: str | None = None
    working_start: str | None = None
    working_end: str | None = None


class DoctorProfileResponse(DoctorProfileBase):
    id:int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class DoctorDetailResponse(DoctorProfileResponse):
    user: UserResponse