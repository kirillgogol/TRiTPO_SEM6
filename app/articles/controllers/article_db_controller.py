from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.articles.models.article_db_models import Article
from app.articles.models import article_api_models
from app.users.models import user_db_models
from app.users.models import user_api_models
from app.authentication import oauth2
from app.logging import logger
from sqlalchemy import exc
from app.file_worker import write_file


class ArticleDBController:

    @classmethod
    def create_article(cls, request: article_api_models.Article, file, background_tasks, 
    current_user: user_api_models.User, db: Session = Depends(get_db)):
        try:
            user = db.query(user_db_models.User).filter(user_db_models.User.email == current_user.email).first()
            if file:
                new_article = Article(**request.dict(), user_id=user.id, file=file.filename)
                background_tasks.add_task(write_file, file)
                db.add(new_article)
                db.commit()
                return new_article
            else:
                new_article = Article(**request.dict(), user_id=user.id)
                db.add(new_article)
                db.commit()
                return new_article

        except exc.SQLAlchemyError as e:
                logger.error(e.__traceback__)
                raise e

    @classmethod
    def show_articles(cls, db: Session = Depends(get_db)):
        return db.query(Article).all()

    @classmethod
    def show_article(cls, id: int, db: Session = Depends(get_db)):
        return db.query(Article).filter(Article.id == id).first()


    @classmethod
    def delete_article(cls, id: int, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id)
            article.delete(synchronize_session=False)
            db.commit()
            logger.info(f"Article with id={id} successfully deleted")
            return {'detail': 'The article was deleted successfully'}
        except exc.SQLAlchemyError as e:
            logger.error(e.__traceback__)
            raise e

    
    @classmethod
    def update_article(cls, id: int, request: article_api_models.Article,
        user: user_db_models.User, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id).first()

            article.title = request.title
            article.brief_description = request.brief_description
            article.url = request.url
            article.language = request.language
            article.category = request.category
            article.user_id = user.id
            db.commit()
            logger.info(f"Article with id={id} successfully updated")
            return article
        except exc.SQLAlchemyError as e:
            logger.error(e.__traceback__)
            raise e
