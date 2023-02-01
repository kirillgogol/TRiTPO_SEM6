from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from datetime import datetime
from sqlalchemy.orm import Session
from app.articles.models.article_db_models import Article
from app.articles.models import article_api_models
from app.users.models import user_db_models
from app.users.models import user_api_models
from app.authentication import oauth2
from app.logging import logger
from sqlalchemy import exc
from app.file_worker import write_file
from app.exceptions import *
import os 


class ArticleDBController:

    @classmethod
    def create_article(cls, request: article_api_models.Article, file, background_tasks, 
    current_user: user_api_models.User, db: Session = Depends(get_db)):
        try:
            user = db.query(user_db_models.User).filter(user_db_models.User.email == current_user.email).first()                
            if file:              
                new_article = Article(**request.dict(), user_id=user.id, file=file.filename)
                hash_part = datetime.now()
                file_hash = str(hash_part.microsecond * hash_part.second) + file.filename
                new_article.file_hash = file_hash
                file.filename = file_hash
                background_tasks.add_task(write_file, file)
            else:
                new_article = Article(**request.dict(), user_id=user.id)
            db.add(new_article)
            db.commit()
            return new_article

        except exc.SQLAlchemyError as e:
                logger.error(e._message())
                raise e

    @classmethod
    def get_all_articles(cls, db: Session = Depends(get_db)):
        return db.query(Article).all()

    @classmethod
    def get_article(cls, id: int, db: Session = Depends(get_db)):
        return db.query(Article).filter(Article.id == id).first()


    @classmethod
    def delete_article(cls, id: int, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id)
            if article.first().file:
                os.remove(f'files/{article.first().file_hash}')
            article.delete(synchronize_session=False)
            db.commit()
            logger.info(f"Article with id={id} successfully deleted")
            return {'detail': 'The article was deleted successfully'}
        except exc.SQLAlchemyError as e:
            logger.error(e._message())
            raise e

    
    @classmethod
    def update_article(cls, id: int, request: article_api_models.Article, file, background_tasks, 
        user: user_db_models.User, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id).first()
            article.title = request.title
            article.brief_description = request.brief_description
            article.url = request.url
            article.language = request.language
            article.category = request.category
            article.user_id = user.id
            if article.file:
                os.remove(f'files/{article.file_hash}')
            if file:
                article.url = None
                article.file = file.filename
                hash_part = datetime.now()
                file_hash = str(hash_part.microsecond * hash_part.second) + file.filename
                article.file_hash = file_hash
                file.filename = file_hash
                background_tasks.add_task(write_file, file)
            else:
                article.file = None
                article.file_hash = None
            db.commit()
            logger.info(f"Article with id={id} successfully updated")
            return article
        except exc.SQLAlchemyError as e:
            logger.error(e._message())
            raise e


    @classmethod
    def download_file(cls, id: int, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id).first()
        if not article:
            raise ArticleNotFoundError
        return {
            "path": f"files/{article.file_hash}",
            "filename": article.file
        }
