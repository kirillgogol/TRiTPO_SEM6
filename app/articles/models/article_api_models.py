from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date
import app.users.models.user_api_models as api_user


class Tag(BaseModel):
    title: str


class ShowTag(Tag):
    id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Catgory(BaseModel):
    title: str


class ShowCatgory(Catgory):
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

    tags: List[Tag]
    categories: List[Catgory]

    class Config:
        arbitrary_types_allowed = True


class ShowArticle(BaseModel):
    title: str
    brief_description: str
    content: str
    url: str
    language: Literal["English", "Russian"]
    user_id: int
    tags: list
    categories: list

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
