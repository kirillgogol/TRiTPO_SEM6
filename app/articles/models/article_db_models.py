from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db_config import Base
from datetime import datetime
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship


class Article(Base):
    __tablename__ = 'articles'

    CATEGORIES = [
        ("devops", "devops"),
        ("python", "python"), 
        ("javascript", "javascript"),
        ("testing", "testing"),
        ("other", "other")    
    ]

    LANGUAGES = [
        ("English", "английский"),
        ("Russian", "русский")
    ]

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    brief_description = Column(String)
    views = Column(Integer, default=0)
    date_published = Column(DateTime, default=datetime.now)
    url = Column(String)
    file = Column(String)
    language = Column(ChoiceType(LANGUAGES))
    category = Column(ChoiceType(CATEGORIES))

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    author = relationship("User", back_populates='articles')
