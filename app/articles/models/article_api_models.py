from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date
import app.users.models.user_api_models as api_user


class Tag(BaseModel):
    title: str

    class Config:
        orm_mode = True


class ShowTag(Tag):
    id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Category(BaseModel):
    title: str

    class Config:
        orm_mode = True


class ShowCatgory(Category):
    id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Article(BaseModel):
    title: str
    brief_description: str
    content: str
    url: str
    language: Literal["English", "Russian"]
    user_id: int

    tags: list[Tag]
    categories: list[Category]

    class Config:
        arbitrary_types_allowed = True


class ShowArticle(BaseModel):
    title: str
    brief_description: str
    content: str
    url: str
    language: Literal["English", "Russian"]
    # user_id: int
    author: api_user.ShowUser
    tags: list[Tag]
    categories: list[Category]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
