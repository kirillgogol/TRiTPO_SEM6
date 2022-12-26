from fastapi import Depends, status
from app.users.models.user_api_models import User
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.users.controllers.user_db_controller import UserDBController, HTTPException
from app.authentication.token import is_valid_password
from app.logging import logger
from app.exceptions import *

class UserAPIController:

    @classmethod
    def create_user(cls, request: User, db: Session = Depends(get_db)): 
        try: 
            if is_valid_password(request.password) is False:
                raise InvalidPasswordError     
            if UserDBController.is_email_not_exist(request.email, db):
                new_user = UserDBController.create_user(request, db)
                return new_user
            else:
                raise ExistingEmailError
        except InvalidPasswordError as e:
            logger.error("Invalid password error")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Password must contain more than 6 non-spaced symbols")
        except ExistingEmailError as e:
            logger.error(f"User with email {request.email} is already exist")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"User with email {request.email} is already exist")

    
    @classmethod
    def get_all_users(cls, db: Session = Depends(get_db)):
        users = UserDBController.get_all_users(db)
        if len(users) > 0:
            logger.info(f"Users are successfully founded")
        else:
            logger.info(f"No registered users")
        return users


    @classmethod
    def get_user(cls, id: int, db: Session = Depends(get_db)):
        try:
            user = UserDBController.get_user(id, db)
            if not user:
                raise UserNotFoundError
            logger.info(f"User with id={id} successfully founded")
            return user
        except UserNotFoundError as e:
            logger.error(f'User with id={id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={id} is not found')
        
  
    @classmethod
    def update_user(cls, id: int, request: User, db: Session = Depends(get_db)):
        try:
            user = UserDBController.get_user(id, db)
            if not user:
                raise UserNotFoundError
            
            if user.email == request.email or UserDBController.is_email_not_exist(request.email, db):            
                return UserDBController.update_user(id, request, db)
            else:
                raise ExistingEmailError

        except UserNotFoundError as e:
            logger.error(f'User with id={id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={id} is not found')
        except ExistingEmailError as e:
            logger.error(f"User with email {request.email} is already exist")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"User with email {request.email} is already exist")

    
    @classmethod
    def delete_user(cls, id: int, db: Session = Depends(get_db)):
        try:
            user = UserDBController.get_user(id, db)
            if not user:
               raise UserNotFoundError 
            return UserDBController.delete_user(id, db)
        except UserNotFoundError as e:
            logger.error(f"User with id={id} is not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={id} is not found')