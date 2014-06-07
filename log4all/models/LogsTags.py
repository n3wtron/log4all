from sqlalchemy import Column, Integer, ForeignKey, String, Index
from sqlalchemy.orm import relation, relationship
from log4all.models import Base

__author__ = 'igor'


class LogsTags(Base):
    __tablename__ = 'logs_tags'
    log_id = Column(Integer, ForeignKey('logs.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    tag = relationship('Tag')
    log = relationship('Log')
    value = Column(String)
    Index('idx_logs_tags_value', tag_id, value)

    def __init__(self, value):
        self.value = value
