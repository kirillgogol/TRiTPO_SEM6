from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table
from app.db_config import Base
from datetime import datetime
# from app.users.models.db_models import User
from sqlalchemy.orm import relationship


article_category = Table('article_category',
    Base.metadata,
    Column('article_id', ForeignKey('articles.id', ondelete="CASCADE"), primary_key=True),
    Column('category_id', ForeignKey('categories.id', ondelete="CASCADE"), primary_key=True),
    )

article_tag = Table('article_tag',
    Base.metadata,
    Column('article_id', ForeignKey('articles.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True),
    )


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    brief_description = Column(String)
    content = Column(String, nullable=False)
    views = Column(Integer, default=0)
    date_published = Column(Date, default=datetime.now)
    url = Column(String, nullable=False)
    language = Column(String(20))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

    categories = relationship("Category", secondary=article_category, back_populates='articles', cascade="delete, all")
    tags = relationship("Tag", secondary=article_tag, back_populates='articles', cascade="delete, all")


class Category(Base):
    __tablename__ = 'categories'

    id = id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)

    articles = relationship("Article", secondary=article_category, back_populates='categories')


class Tag(Base):
    __tablename__ = 'tags'

    id = id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)

    articles = relationship("Article", secondary=article_tag, back_populates='tags')
