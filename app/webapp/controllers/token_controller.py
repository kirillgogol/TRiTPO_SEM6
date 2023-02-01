from fastapi import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db_config import get_db
from app.users.models.user_db_models import User
from app.authentication.token import verify_access, refresh_token
from app.exceptions import *
from app.webapp.models.verifying_models import VerifyingModel


def verify_tokens(token, db: Session):
    try:
        user = verify_access(token['access_token'])
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise UserNotFoundError
        return VerifyingModel(user=db_user, access_token=token['access_token'])
    except AccessTokenExpiredError:
        new_token = refresh_token(token['refresh_token'])
        user = verify_access(new_token)
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise UserNotFoundError
        return VerifyingModel(user=db_user, access_token=new_token)
