from bson import ObjectId

from log4all.util.json_util import jsonizer


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

from datetime import datetime


class User():
    def __init__(self, email=None, name=None, password=None, active=False, groups=[], permissions=[]):
        self._id = None
        self.email = email
        self.name = name
        self.password = password
        self.active = active
        self.groups = groups
        self.permissions = permissions
        self._dt_insert = datetime.now()

    def __json__(self, request=None):
        json = {
            'email': self.email,
            'name': self.name,
            'password': self.password,
            'active': self.active,
            'groups': self.groups,
            'permissions': self.permissions,
            '_dt_insert': jsonizer(self._dt_insert)
        }
        if self._id is not None:
            json['_id'] = self._id
        return json

    @staticmethod
    def from_bson(bson):
        if bson is None:
            return None
        user = User(email=bson.get('email'),
                    name=bson.get('name'),
                    password=bson.get('password'),
                    active=jsonizer(bson.get('active')),
                    groups=bson.get('groups'),
                    permissions=bson.get('permissions'))
        user._id = str(bson.get('_id'))
        user._dt_insert = jsonizer(bson.get('_dt_insert'))
        return user

    @staticmethod
    def init(db):
        db.users.ensure_index('_id', unique=True)
        db.users.ensure_index('email', unique=True)

    def save(self, db):
        json = self.__json__()
        if self._id is not None:
            del json['_id']
            db.users.update({'_id': ObjectId(self._id)}, json, w=1)
        else:
            id = db.users.insert(json, w=1)
            if id is not None:
                self._id = str(id)


    @staticmethod
    def get(db, src_query={}):
        return User.from_bson(db.users.find_one(src_query))

    @staticmethod
    def delete(db, user_id):
        db.users.remove(user_id)

    @staticmethod
    def search(db, src_query={}):
        for dbApp in db.users.find(src_query):
            yield User.from_bson(dbApp)