from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.articles.models.article_api_models import Article
from app.users.models.user_api_models import User
from app.authentication import oauth2
from app.articles.controllers.article_db_controller import ArticleDBController
from app.users.controllers.user_db_controller import UserDBController
from app.logging import logger
from app.exceptions import *


class ArticleAPIController:

    @classmethod
    def create_article(cls, title, brief_description, language, category, url, 
    background_tasks, file, current_user: User, db: Session = Depends(get_db)):
        try:
            if len(str(url)) > 0:
                new_article = Article(
                    title=title,
                    brief_description=brief_description,
                    language=language,
                    url=url,
                    category=category
                )
                return ArticleDBController.create_article(new_article, file, background_tasks, current_user, db)
            else:
                raise EmptyURLError

        except EmptyURLError as e:
            logger.error(f"Article url should not be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Article url should not be empty")


    @classmethod
    def get_all_articles(cls, db: Session = Depends(get_db)):
        articles = ArticleDBController.show_articles(db)
        if len(articles) > 0:
            logger.info(f"All articles were successfully founded")
        else:
            logger.info(f"No published articles")
        return articles

    @classmethod
    def get_article(cls, id: int, db: Session = Depends(get_db)):
        try:
            article = ArticleDBController.show_article(id, db)
            if not article:
                raise ArticleNotFoundError
            logger.info(f"Article with id={id} was successfully founded")
            return article

        except ArticleNotFoundError as e:
            logger.error(f"Article with id={id} is not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Article with id={id} is not found')

    @classmethod
    def update_article(cls, id: int, request: Article, current_user: User, db: Session = Depends(get_db)):
        try:
            article = ArticleDBController.show_article(id, db)
            if not article:
                raise ArticleNotFoundError
            user = UserDBController.get_user(article.user_id, db)
            if current_user.email == user.email:
                return ArticleDBController.update_article(id, request, user, db)
            else:
                raise UnothorizedAccessError

        except ArticleNotFoundError as e:
            logger.error(f"Article with id={id} is not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Article with id={id} is not found')

        except UnothorizedAccessError as e:
            logger.error(f'Updating provides only for author of the article with id={id}')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail=f'Updating provides only for author of the article with id={id}')

    @classmethod
    def delete_article(cls, id: int, current_user: User, db: Session = Depends(get_db)):
        try:
            article = ArticleDBController.show_article(id, db)
            if not article:
                raise ArticleNotFoundError

            user = UserDBController.get_user(article.user_id, db)
            if current_user.email == user.email:
                return ArticleDBController.delete_article(id, db)
            else:
                raise UnothorizedAccessError

        except ArticleNotFoundError as e:
            logger.error(f"Article with id={id} is not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Article with id={id} is not found')

        except UnothorizedAccessError as e:
            logger.error(f'Updating provides only for author of the article with id={id}')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail=f'Updating provides only for author of the article with id={id}')

        