from bson import ObjectId

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


class Group():
    def __init__(self, name, description, permissions=[]):
        self._id = None
        self.name = name
        self.description = description
        self.permissions = permissions

    def __json__(self, request=None):
        json = {'name': self.name, 'description': self.description, 'permissions': self.permissions}
        if self._id is not None:
            json['_id'] = self._id
        return json

    @staticmethod
    def from_bson(bson):
        if bson is None:
            return None
        group = Group(bson['name'], bson.get('description'), bson.get('permissions'))
        group._id = str(bson['_id'])
        return group

    @staticmethod
    def init(db):
        db.groups.ensure_index('_id', unique=True)
        db.groups.ensure_index('name', unique=True)

    def save(self, db):
        json = self.__json__()
        if self._id is not None:
            del json['_id']
            db.groups.update({'_id': ObjectId(self._id)}, json, w=1)
        else:
            id = db.groups.insert(json, w=1)
            if id is not None:
                self._id = str(id)


    @staticmethod
    def get(db, src_query={}):
        return Group.from_bson(db.groups.find_one(src_query))

    @staticmethod
    def delete(db, group_id):
        db.groups.remove(group_id)

    @staticmethod
    def search(db, src_query={}):
        for dbApp in db.groups.find(src_query):
            yield Group.from_bson(dbApp)