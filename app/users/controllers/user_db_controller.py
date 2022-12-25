from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.users.models import user_api_models, user_db_models
from passlib.context import CryptContext
from app.logging import logger
from sqlalchemy import exc


class UserDBController:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_user(cls, request: user_api_models.User, db: Session = Depends(get_db)):
        try:
            encrypted_password = cls.pwd_context.hash(request.password)
            new_user = user_db_models.User(
                username = request.username,
                email = request.email,
                password = encrypted_password
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"User with email {request.email} successfully created")
            return new_user
        except exc.SQLAlchemyError as e:
            logger.error(e.__traceback__)
            raise e


    @classmethod
    def get_all_users(cls, db: Session = Depends(get_db)):
        users = db.query(user_db_models.User).all()
        return users

    
    @classmethod
    def get_user(cls, id: int, db: Session = Depends(get_db)):
        user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
        return user.first()


    @classmethod
    def delete_user(cls, id: int, db: Session = Depends(get_db)):
        try:
            user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
            user.delete(synchronize_session=False)
            db.commit()
            logger.info(f"User with id={id} successfully deleted")
            return {"detail": f"User with id={id} was successfully deleted"}
        except exc.SQLAlchemyError as e:
            logger.error(e.__traceback__)
            raise e

    
    @classmethod
    def update_user(cls, id: int, request: user_api_models.User, db: Session = Depends(get_db)):
        try:
            user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
            user.update(request.dict(), synchronize_session=False)
            db.commit()
            logger.info(f'User with id={id} successfully updated')
            return user.first()
        except exc.SQLAlchemyError as e:
            logger.error(e.__traceback__)
            raise e

    @classmethod
    def is_email_not_exist(cls, email, db: Session = Depends(get_db)):

        user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()
        return user is None