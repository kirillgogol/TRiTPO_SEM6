from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.authentication import schemas, token
from app.users.models.user_db_models import User
from app.db_config import get_db


router = APIRouter(prefix='/auth', tags=['authentication'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form = await request.form()

    user = db.query(User).filter(User.email == request.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'No user with email {request.username}')

    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Incorrect password')

    access_token_expires = token.timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = token.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = token.timedelta(minutes=token.REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = token.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
