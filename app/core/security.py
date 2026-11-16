import jwt
import bcrypt
from datetime import timedelta, timezone, datetime
from app.core import settings




def hash_password(password:str) -> str:
    hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return hash_pw


def verify_password(plain_password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
 


def create_access_token(data:dict, expires_delta:timedelta | None = None) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode["exp"] = expire

    return jwt.encode(to_encode,settings.SECRET_KEY, algorithm=settings.ALGORITHM)