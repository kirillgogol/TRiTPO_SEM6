from pydantic import BaseModel
from typing import List


class User(BaseModel):
    username: str
    email: str
    password: str

  
class ShowUser(BaseModel):
    # id: int
    username: str
    email: str

    class Config:
        orm_mode = True