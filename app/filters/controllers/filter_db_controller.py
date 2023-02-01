from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.db_config import get_db
from app.filters.models.filter_api_models import ArticleFilter
from app.articles.models.article_db_models import Article


class FilterDBController:

    @classmethod
    def get_filtered_articles(cls, filters: ArticleFilter, db: Session = Depends(get_db)):

        query = db.query(Article)

        if filters.category != "Any":
            query = query.filter(Article.category == filters.category)

        if filters.title:
            query = query.filter(Article.title.contains(filters.title))

        if filters.language != "Any":
            query = query.filter(Article.language == filters.language)

        if filters.author_email is not None and filters.author_email != "":
            query = query.filter(Article.author.has(email = filters.author_email))

        return query.all()