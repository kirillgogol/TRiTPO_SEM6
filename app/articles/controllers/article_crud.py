from fastapi import Depends, status, HTTPException
from app.db_config import get_db
from sqlalchemy.orm import Session
from app.articles.models.article_db_models import Article, Tag, Category, article_category, article_tag
from app.articles.models import article_api_models
from app.users.models import user_db_models


class ArticleController:

    @classmethod
    def create_article(cls, request: article_api_models.Article, db: Session = Depends(get_db)):
        # user = db.query(user_db_models.User).filter(user_db_models.User.id == request.user_id)

        # if not user.first():
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id={request.user_id} found')
        try:
            transaction = db.begin()

            new_article = Article(
                title = request.title,
                brief_description = request.brief_description,
                content = request.content,
                url = request.url,
                language = request.language,
                user_id = request.user_id
            )
            db.add(new_article)
            db.flush()
            existing_tags = [tag['title'] for tag in db.query(Tag.title).all()]

            for tag in request.tags:
                if tag.title not in existing_tags:
                    new_tag = Tag(title = tag.title)
                    new_article.tags.append(new_tag)
                else:
                    new_tag = db.query(Tag).filter(Tag.title == tag.title).first()
                    new_article.tags.append(new_tag)

            existing_categories = [category['title'] for category in db.query(Category.title).all()]

            for category in request.categories:
                if category.title not in existing_categories:
                    new_category = Category(title = category.title)  
                    new_article.categories.append(new_category)  
                else:
                    new_category = db.query(Category).filter(Category.title == category.title).first()
                    new_article.categories.append(new_category)

            transaction.commit()   
            return {'server response': status.HTTP_201_CREATED}
        except Exception:
            transaction.rollback()
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
    def delete_useless_tags_and_categories(cls, db: Session = Depends(get_db)):
        query = "SELECT article_tag.tag_id FROM article_tag"
        useful_tags_raw = db.execute(query)  
        useful_tags = [t[0] for t in useful_tags_raw]    
        current_tags = db.query(Tag).all()

        for tag in current_tags:
            if tag.id not in useful_tags:
                db.delete(tag)

        query = "SELECT article_category.category_id FROM article_category"
        useful_categoties_raw = db.execute(query)
        useful_categoties = [c[0] for c in useful_categoties_raw]
        current_categories = db.query(Category).all()

        for category in current_categories:
            if category.id not in useful_categoties:
                db.delete(category)
        db.flush()
        # db.commit()

    @classmethod
    def delete_article(cls, id: int, db: Session = Depends(get_db)):
        article = db.query(Article).filter(Article.id == id)
        if not article.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'article with id={id} not found')
        article.delete(synchronize_session=False)
        db.commit()
        ArticleController.delete_useless_tags_and_categories(db)
        return {'server response': status.HTTP_200_OK}

    
    @classmethod
    def update_article(cls, id: int, request: article_api_models.Article, db: Session = Depends(get_db)):
        try:
            article = db.query(Article).filter(Article.id == id).first()
            if not article:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'article with id={id} not found')

            article.title = request.title
            article.brief_description = request.brief_description
            article.content = request.content
            article.url = request.url
            article.language = request.language
            article.tags.clear()
            article.categories.clear()
            db.flush()

            ArticleController.delete_useless_tags_and_categories(db)

            existing_tags = [tag['title'] for tag in db.query(Tag.title).all()]
            
            for tag in request.tags:
                if tag.title not in existing_tags:
                    new_tag = Tag(title=tag.title)
                    article.tags.append(new_tag)
                else:
                    new_tag = db.query(Tag).filter(Tag.title == tag.title).first()
                    article.tags.append(new_tag)
                

            existing_categories = [category['title'] for category in db.query(Category.title).all()]
            
            for category in request.categories:
                if category.title not in existing_categories:
                    new_category = Category(title=category.title)
                    article.categories.append(new_category)
                else:
                    new_category = db.query(Category).filter(Category.title == category.title).first()
                    article.categories.append(new_category)

            db.commit()
            return {'server response': status.HTTP_202_ACCEPTED}
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Article is not updated')
