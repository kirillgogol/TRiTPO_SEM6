from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from app.db_config import get_db, Base
import app.users.models.user_api_models as user_api_models
import app.users.models.user_db_models as user_db_models
from app.users.controllers.user_db_controller import UserDBController
from app.users.controllers.user_api_controller import UserAPIController
from app.authentication import oauth2
from app.authentication.token import verify_access, refresh_token

router = APIRouter(
    prefix='/user',
    tags=['users']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(request: user_api_models.User, db: Session = Depends(get_db)):

    return UserAPIController.create_user(request, db)


@router.get('/all', response_model=List[user_api_models.ShowUser])
def get_users(db: Session = Depends(get_db), 
current_user: user_api_models.User = Depends(oauth2.get_current_user)):

    return UserAPIController.get_all_users(db)


@router.get('/{id}', response_model=user_api_models.ShowUser)
def get_user(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):

    return  UserAPIController.get_user(id, db)


@router.delete('/{id}')
def delete_user(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
 
    return UserAPIController.delete_user(id, db)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_user(id: int, request: user_api_models.User, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    
    return UserAPIController.update_user(id, request, db)
