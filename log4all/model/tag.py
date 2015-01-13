import logging

from pymongo import ASCENDING


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Tag:
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __json__(self, request=None):
        return {
            'tag_name': self.tag_name
        }

    @staticmethod
    def init(db):
        db.tags.ensure_index('tag_name', unique=True, dropDups=True)

    @staticmethod
    def bulk_save(db, tags):
        db.tags.insert([tag.__json__() for tag in tags])

    @staticmethod
    def search(db, src_query={}):
        for tag in db.tags.find(src_query, sort=[('tag_name', ASCENDING)]):
            yield Tag(tag['tag_name'])

    def save(self, db):
        db.tags.insert(self.json())