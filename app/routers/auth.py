from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

DbSession = Annotated[Session, Depends(get_db)]

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in : UserCreate, db: DbSession) -> User:
    email = db.execute(select(User).filter_by(email=user_in.email)).scalar_one_or_none()

    if email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı!"
        )

    hashed_pw = hash_password(user_in.password)

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        hashed_password=hashed_pw,
        role=UserRole.PATIENT 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession
):
    user = db.execute(select(User).filter_by(email=form_data.username)).scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı e-posta veya şifre!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanıcı hesabı pasif durumda."
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Giriş yapmış olan kullanıcının kendi profil bilgilerini döner."""
    return current_user