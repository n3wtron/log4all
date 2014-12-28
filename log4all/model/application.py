import logging

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Application:
    def __init__(self, name, description=None, configuration=None):
        self.name = name
        self.description = description
        self.configuration = configuration

    def json(self):
        return {
            'name': self.name,
            'description': self.description,
            'configuration': self.configuration
        }

    @staticmethod
    def init(db):
        db.applications.ensure_index('name', unique=True)

    def save(self, db):
        db.applications.insert(self.json())

    @staticmethod
    def search(db, src_query={}, single=False):
        if not single:
            return db.applications.find(src_query)
        else:
            return db.applications.find_one(src_query)