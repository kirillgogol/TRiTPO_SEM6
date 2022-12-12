from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.articles.models.article_db_models import Article
from app.articles.models import article_api_models
from app.users.models import user_db_models
from app.users.models import user_api_models
from app.authentication import oauth2


class ArticleController:

    @classmethod
    def create_article(cls, request: article_api_models.Article, db: Session = Depends(get_db),
    current_user: user_api_models.User = Depends(oauth2.get_current_user)):
        # print(current_user)
        user = db.query(user_db_models.User).filter(user_db_models.User.email == current_user.email).first()

        # if not user:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={request.user_id} found')
        try:
            new_article = Article(
                title = request.title,
                brief_description = request.brief_description,
                url = request.url,
                language = request.language,
                # user_id = request.user_id,
                category = request.category,
                user_id = user.id
            )
            db.add(new_article)
            db.commit()
            return {'detail': 'the article was created successfully'}
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Article is not created')

    @classmethod
    def show_articles(cls, db: Session = Depends(get_db)):
        return db.query(Article).all()

    @classmethod
    def show_article(cls, id: int, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id)
        if not article.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        return article


    @classmethod
    def delete_article(cls, id: int, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id)
        if not article.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'article with id={id} not found')
        article.delete(synchronize_session=False)
        db.commit()
        return {'detail': 'The article was updated successfully'}

    
    @classmethod
    def update_article(cls, id: int, request: article_api_models.Article, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id).first()
            if not article:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Article with id={id} not found')

            article.title = request.title
            article.brief_description = request.brief_description
            article.url = request.url
            article.language = request.language
            article.user_id = request.user_id
            article.category = request.category
            db.commit()
            return {'detail': 'The article was updated successfully'}
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='The article was not updated')
