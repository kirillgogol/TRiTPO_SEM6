from pydantic import BaseModel, HttpUrl
from typing import List, Literal


class ArticleFilter(BaseModel):
    title: str = None
    language: Literal["Any", "English", "Russian"]
    category: Literal['Any', 'python', 'devops', 'javascript', 'testing', 'other']
    author_email: str = None
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        use_enum_values = True