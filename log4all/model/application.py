import logging

from bson import ObjectId


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Application:
    def __init__(self, name, token=None, description=None, configuration=None):
        self._id = None
        self.name = name
        self.token = token
        self.description = description
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = {
                'DEBUG': {
                    'archive': 0,
                    'delete': 30
                },
                'INFO': {
                    'archive': 30,
                    'delete': 60
                },
                'WARNING': {
                    'archive': 60,
                    'delete': 180
                },
                'ERROR': {
                    'archive': 90,
                    'delete': 365
                }
            }

    def __json__(self, request=None):
        json = {
            'name': self.name,
            'token': self.token,
            'description': self.description,
            'configuration': self.configuration
        }
        if self._id is not None:
            json['_id'] = self._id
        return json

    @staticmethod
    def from_bson(bson):
        app = Application(bson['name'], bson.get('token'), bson.get('description'), bson.get('configuration'))
        app._id = str(bson['_id'])
        return app

    @staticmethod
    def init(db):
        db.applications.ensure_index('_id', unique=True)
        db.applications.ensure_index('name', unique=True)

    def save(self, db):
        json = self.__json__()
        if self._id is not None:
            del json['_id']
            db.applications.update({'_id': ObjectId(self._id)}, json, w=1)
        else:
            id = db.applications.insert(json, w=1)
            if id is not None:
                self._id = str(id)


    @staticmethod
    def get(db, src_query={}):
        return Application.from_bson(db.applications.find_one(src_query))

    @staticmethod
    def delete(db, id):
        db.applications.remove(id)

    @staticmethod
    def search(db, src_query={}):
        for dbApp in db.applications.find(src_query):
            yield Application.from_bson(dbApp)