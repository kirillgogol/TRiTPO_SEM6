from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.db_config import get_db, Base
import app.users.models.user_api_models as user_api_models
import app.users.models.user_db_models as user_db_models
from app.users.controllers.user_crud import UserController


router = APIRouter(
    prefix='/user',
    tags=['users']
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=['users'])
def create_user(request: user_api_models.User, db: Session = Depends(get_db)):
    
    return UserController.create_user(request, db)


@router.get('/', response_model=List[user_api_models.ShowUser], tags=['users'])
def get_users(db: Session = Depends(get_db)):

    return  UserController.show_users(db)

@router.get('/{id}', response_model=user_api_models.ShowUser, tags=['users'])
def get_users(id: int, db: Session = Depends(get_db)):

    return  UserController.show_user(id, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['users'])
def delete_user(id: int, db: Session = Depends(get_db)):
 
    return UserController.delete_user(id, db)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['users'])
def update_user(id: int, request: user_api_models.User, db: Session = Depends(get_db)):
    
    return UserController.update_user(id, request, db)
