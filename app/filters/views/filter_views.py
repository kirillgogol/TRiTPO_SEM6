from fastapi import APIRouter, Depends, status
from typing import Literal
from sqlalchemy.orm import Session
from app.db_config import get_db
from app.authentication import oauth2
from app.articles.models.article_api_models import ShowArticle
from typing import List
from app.users.models.user_api_models import User
from app.filters.models.filter_api_models import ArticleFilter
from app.filters.controllers.filter_api_controller import FilterAPIController


router = APIRouter(
    prefix='/filters',
    tags=['filters']
)


@router.post('/', response_model=List[ShowArticle], status_code=status.HTTP_200_OK)
def get_filtered_articles(
    language: Literal["Any", "English", "Russian"],
    category: Literal['Any', 'python', 'devops', 'javascript', 'testing', 'other'],
    title: str = None,
    author_email: str = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(oauth2.get_current_user)):

    return FilterAPIController.get_filtered_articles(language, category, title, author_email, db)