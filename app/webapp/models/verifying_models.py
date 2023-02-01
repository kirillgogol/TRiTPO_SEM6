from pydantic import BaseModel
from app.users.models.user_db_models import User


class VerifyingModel(BaseModel):
    user: User
    access_token: str

    class Config:
        arbitrary_types_allowed = True