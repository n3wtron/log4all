from log4all.models import Base

__author__ = 'igor'
from sqlalchemy import Column, Integer, Unicode


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), unique=True)
