from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.users.models import user_api_models, user_db_models
from passlib.context import CryptContext


class UserController:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_user(cls, request: user_api_models.User, db: Session = Depends(get_db)):
        encrypted_password = cls.pwd_context.hash(request.password)
        new_user = user_db_models.User(
            username = request.username,
            email = request.email,
            password = encrypted_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


    @classmethod
    def show_users(cls, db: Session = Depends(get_db)):
        users = db.query(user_db_models.User).all()
        return users

    
    @classmethod
    def show_user(cls, id: int, db: Session = Depends(get_db)):
        user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        return user.first()


    @classmethod
    def delete_user(id: int, db: Session = Depends(get_db)):
        user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        user.delete(synchronize_session=False)
        db.commit()
        return "Successfully deleted"

    
    @classmethod
    def update_user(cls, id: int, request: user_api_models.User, db: Session = Depends(get_db)):
        user = db.query(user_db_models.User).filter(user_db_models.User.id == id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        user.update(request.dict(), synchronize_session=False)
        db.commit()
        return user.first()