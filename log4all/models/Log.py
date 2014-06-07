import datetime
from sqlalchemy.orm import relationship, class_mapper
from log4all.models.LogsTags import LogsTags

__author__ = 'igor'
from sqlalchemy import Column, Integer, Date, Text
from log4all.models import Base


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dt_insert = Column(Date, default=datetime.datetime.now())
    message = Column(Text)
    tags = relationship('LogsTags', backref='logs', lazy='joined')

    def as_dict(self):
        columns = [c.key for c in class_mapper(self.__class__).columns]
        result = dict(('_'+c, str(getattr(self, c))) for c in columns)
        for tag in self.tags:
            result[tag.tag.name] = tag.value
        return result