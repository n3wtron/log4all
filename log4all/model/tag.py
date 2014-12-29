import logging

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Tag:
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __json__(self,request = None):
        return {
            'tag_name': self.tag_name
        }

    @staticmethod
    def init(db):
        db.tags.ensure_index('tag_name', unique=True)

    @staticmethod
    def bulk_save(db, tags):
        db.tags.insert([tag.__json__() for tag in tags])

    def save(self, db):
        db.tags.insert(self.json())