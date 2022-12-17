from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, MetaData
from app.db_config import Base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(EmailType, nullable=False, unique=True)
    password = Column(String, nullable=False)

    articles = relationship('Article', back_populates="author", passive_deletes=True)
