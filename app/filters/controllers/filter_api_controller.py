from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.db_config import get_db
from app.filters.models.filter_api_models import ArticleFilter
from app.filters.controllers.filter_db_controller import FilterDBController


class FilterAPIController:

    @classmethod
    def get_filtered_articles(cls, language, category, title, author_email, db: Session = Depends(get_db)):

        filters = ArticleFilter(
            language=language,
            category=category,
            title=title,
            author_email=author_email
        )
        
        return FilterDBController.get_filtered_articles(filters, db)