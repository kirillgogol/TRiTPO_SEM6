from fastapi import HTTPException, status
from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
from app.authentication import schemas
from app.settings import settings
from app.exceptions import *

SECRET_KEY = settings.SECRET_KEY
SECRET_REFRESH_KEY = settings.SECRET_REFRESH_KEY

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES


def is_valid_password(password: str):
    if len(password.replace(' ', '')) >= 6:
        return True
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_REFRESH_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access(token: str):

    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise AccessTokenExpiredError
        token_data = schemas.TokenData(email=email)
        return token_data
    except JWTError:
        raise AccessTokenExpiredError

    
def refresh_token(refresh_token: str):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Refresh token is not active",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(refresh_token, SECRET_REFRESH_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise RefreshTokenExpiredError

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        new_access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        return new_access_token
    except JWTError:
        raise RefreshTokenExpiredError
