from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.articles.models.article_db_models import Article, article_tag, article_category, Tag, Category
from app.articles.models import article_api_models
from app.users.models import user_db_models


class ArticleController:

    @classmethod
    def create_article(cls, request: article_api_models.Article, db: Session = Depends(get_db)):
        user = db.query(user_db_models.User).filter(user_db_models.User.id == request.user_id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={request.user_id} found')

        new_article = Article(
            title = request.title,
            brief_description = request.brief_description,
            content = request.content,
            url = request.url,
            language = request.language,
            user_id = request.user_id
        )
        db.add(new_article)
        db.commit()

        existing_tags = [name[0] for name in db.query(Tag.title).all()]

        for tag in request.tags:

            if tag.name not in existing_tags:
                db.add(Tag(name = tag.name))
                db.commit()
            
            tag_id = db.query(Tag.id).filter(Tag.title == tag.name)
            new_article_tag = article_tag(
                tag_id = tag_id,
                article_id = new_article.id
            )
            db.add(new_article_tag)
            db.commit()
        
        db.refresh(new_article)
        return new_article


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
    def delete_article(id: int, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id)
        if not article.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        article.delete(synchronize_session=False)
        db.commit()
        return "Successfully deleted"

    
    @classmethod
    def update_article(cls, id: int, request: article_api_models.Article, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id)
        if not article.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
        article.update(request.dict(), synchronize_session=False)
        db.commit()
        return article.first()