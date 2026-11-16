from pydantic import EmailStr, BaseModel, ConfigDict
from datetime import datetime
from app.models.enums import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name : str
    phone_number: str | None = None


class UserCreate(UserBase):
    password:str


class UserResponse(UserBase):
    id:int
    role:UserRole
    is_active:bool
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token:str
    token_type:str="bearer"

class TokenData(BaseModel):
    user_id:int | None=None
    role:str | None=None