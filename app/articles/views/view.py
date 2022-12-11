from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.db_config import get_db
import app.articles.models.article_api_models as article_api_models
import app.users.models.user_api_models as user_api_models
import app.articles.models.article_db_models as article_db_models
from app.articles.controllers.article_crud import ArticleController
from app.authentication import oauth2


router = APIRouter(
    prefix='/article',
    tags=['articles']
)

# current_user: str = Depends(oauth2.get_current_user)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=['articles'])
def create_article(request: article_api_models.Article, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):   
    return ArticleController.create_article(request, db, current_user)


@router.get('/', response_model=List[article_api_models.ShowArticle], tags=['articles'])
def get_articles(db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    return ArticleController.show_articles(db)

@router.get('/{id}', response_model=article_api_models.ShowArticle, tags=['articles'])
def get_article(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    return ArticleController.show_article(id, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['articles'])
def delete_article(id: int, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
 
    return ArticleController.delete_article(id, db)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['articles'])
def update_article(id: int, request: article_api_models.Article, db: Session = Depends(get_db),
current_user: user_api_models.User = Depends(oauth2.get_current_user)):
    
    return ArticleController.update_article(id, request, db)
