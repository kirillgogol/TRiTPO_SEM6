from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table
from app.config import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)

    articles = relationship('Article')


class ArticleCategory(Base):
    __tablename__ = 'article_category'

    id = Column(Integer, primary_key=True)
    article_id =  Column(Integer(), ForeignKey("article.id"))
    category_id =  Column(Integer(), ForeignKey("category.id"))

    article = relationship("Article", back_populates='categories')
    category = relationship("Category", back_populates='articles')


class ArticleTag(Base):
    __tablename__ = 'article_tag'

    id = Column(Integer, primary_key=True)
    article_id =  Column(Integer(), ForeignKey("article.id"))
    tag_id =  Column(Integer(), ForeignKey("tag.id"))

    article = relationship("Article", back_populates='tags')
    tag = relationship("Tag", back_populates='articles')


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    brief_description = Column(String)
    content = Column(String, nullable=False)
    views = Column(Integer, default=0)
    date_published = Column(Date, nullable=False)
    url = Column(String, nullable=False)
    language = Column(String(20))

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")

    categories = relationship("ArticleCategory", back_populates='article')
    tags = relationship("ArticleTag", back_populates='article')


class Category(Base):
    __tablename__ = 'category'

    id = id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    articles = relationship("ArticleCategory", back_populates='category')


class Tag(Base):
    __tablename__ = 'tag'

    id = id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    articles = relationship("ArticleTag", back_populates='tag')
