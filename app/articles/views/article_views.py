from fastapi import APIRouter, Depends, status, UploadFile
from starlette.background import BackgroundTasks
from typing import List, Literal, Union
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from app.db_config import get_db
import app.articles.models.article_api_models as article_api_models
import app.users.models.user_api_models as user_api_models
import app.articles.models.article_db_models as article_db_models
from app.articles.controllers.article_db_controller import ArticleDBController
from app.articles.controllers.article_api_controller import ArticleAPIController
from app.authentication import oauth2


router = APIRouter(
    prefix='/article',
    tags=['articles']
)


@router.post('/', response_model=article_api_models.ShowArticle, status_code=status.HTTP_201_CREATED)
def create_article(
    title: str,
    brief_description: str,
    language: Literal["English", "Russian"],
    category: Literal['python', 'devops', 'javascript', 'testing', 'other'],
    background_tasks: BackgroundTasks,
    url: Union[HttpUrl, str, None] = None,
    file: Union[UploadFile, None] = None,
    db: Session = Depends(get_db), 
    current_user: user_api_models.User = Depends(oauth2.get_current_user)
): 

    return ArticleAPIController.create_article(
        title, brief_description, language, category, url, background_tasks, file, current_user, db
    )
    # return ArticleDBController.create_article(request, db, current_user)


@router.get('/all', response_model=List[article_api_models.ShowArticle])
def get_articles(db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    return ArticleAPIController.get_all_articles(db)

@router.get('/{id}', response_model=article_api_models.ShowArticle)
def get_article(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    return ArticleAPIController.get_article(id, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_article(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
 
    return ArticleAPIController.delete_article(id, current_user, db)


@router.put('/{id}', response_model=article_api_models.ShowArticle,
 status_code=status.HTTP_202_ACCEPTED)
def update_article(
    id: int, 
    title: str,
    brief_description: str,
    language: Literal["English", "Russian"],
    category: Literal['python', 'devops', 'javascript', 'testing', 'other'],
    background_tasks: BackgroundTasks,
    url: HttpUrl = None,
    file: Union[UploadFile, None] = None,
    db: Session = Depends(get_db),
    current_user: user_api_models.User = Depends(oauth2.get_current_user)):

    return ArticleAPIController.update_article(
        id, title, brief_description, language,
        category, url, background_tasks, file, current_user, db
    )
    # return ArticleDBController.update_article(id, request, db)


@router.get('/{id}/download_file')
def download_file(id: int, db: Session = Depends(get_db),
    current_user: user_api_models.User = Depends(oauth2.get_current_user)):

    return ArticleAPIController.download_file(id, db)
