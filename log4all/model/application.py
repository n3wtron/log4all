import logging

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Application:
    def __init__(self, name):
        self.name = name

    def json(self):
        return {
            'name': self.name
        }

    @staticmethod
    def init(db):
        db.application.ensure_index('name', unique=True)

    def save(self, db):
        db.application.insert(self.json())

    @staticmethod
    def search(db, src_query):
        return db.application.find(src_query)