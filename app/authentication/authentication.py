from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.authentication import schemas, token
from app.users.models.user_db_models import User
from app.db_config import get_db


router = APIRouter(tags=['authentication'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")


@router.get('/logout', response_class=HTMLResponse)
def logout(request: Request):
    response = RedirectResponse('/login', status_code=307)
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')
    return response


@router.get('/login', response_class=HTMLResponse)
def get_login_from(request: Request):

    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/login')
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    user = db.query(User).filter(User.email == form['email']).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'No user with email {form["email"]}')

    if not pwd_context.verify(form['password'], user.password):
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

    response = templates.TemplateResponse('login.html', {'request': request, 'message': 'successfully logged in'})
    response.set_cookie(key='access_token', value=access_token)
    response.set_cookie(key='refresh_token', value=refresh_token)
    return response
