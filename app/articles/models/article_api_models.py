from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Literal, Union
from datetime import date
from enum import Enum
import app.users.models.user_api_models as api_user


class CategoryEnum():
    categories = [
        'devops',
        'python',
        'javascript',
        'тестирование',
        'другое'
    ]
    # devops = 'devops'
    # python = 'python'
    # javascript = 'javascript'
    # testing = 'тестирование'
    # other = 'другое'


class Catgory(BaseModel):
    title: str


class Article(BaseModel):
    title: str
    brief_description: str
    url: HttpUrl = None
    language: Literal["English", "Russian"]
    category: Literal['python', 'devops', 'javascript', 'testing', 'other']
    # file: Union[str, None] = None
    # user_id: int
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        use_enum_values = True


class ShowArticle(Article):
    id: int
    author: api_user.ShowUser
    file: Union[str, None] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
