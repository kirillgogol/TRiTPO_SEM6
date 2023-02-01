from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.authentication.token import verify_access, refresh_token
from app.exceptions import *


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login', scheme_name="JWT")

def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_access(token)
    # try:
    #     return verify_access(token)
    # except AccessTokenExpiredError as e:
    #     try:
    #         token = refresh_token()
    #         return verify_access(token)
    #     except RefreshTokenExpiredError as e:
    #         return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is expiring")