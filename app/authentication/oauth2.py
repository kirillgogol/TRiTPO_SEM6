from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.authentication import token as Token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token: str = Depends(oauth2_scheme)):
       
    return Token.verify_access(token)