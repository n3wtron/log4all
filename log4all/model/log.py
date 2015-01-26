from datetime import datetime
import logging

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
import re

from log4all.util.json_util import jsonizer
from log4all.util.regexp import add_log_matcher, add_log_regexp, group_notification_regexp, group_notification_matcher


_log = logging.getLogger(__name__)


class Log:
    def __init__(self, application=None, level=None, raw_message=None, message=None, tags=None,
                 notification_groups=None, stack_sha=None, date=datetime.now(), stack=None):
        self._id = None
        self.application = application
        self.raw_message = raw_message
        self.date = date
        self.level = level
        self.message = message
        self.tags = tags
        self.stack = stack
        self.stack_sha = stack_sha
        self.notification_groups = notification_groups
        self._dt_insert = datetime.now()
        self._elaborate_message()

    def _elaborate_message(self):
        if self.message is None and self.raw_message is not None:
            if self.tags is None:
                self.tags = dict()
            raw_tags = add_log_matcher.findall(self.raw_message)
            for raw_tag in raw_tags:
                tag = raw_tag[0][1:]  # removed #
                tag = tag.replace("+", "")
                if len(raw_tag[1]) == 0:
                    tag_value = True
                else:
                    tag_value = raw_tag[3]
                    if tag_value[0] == '"' and tag_value[-1] == '"':
                        tag_value = tag_value[1:-1]
                self.tags[tag] = tag_value

            # Cleaning message
            self.message = re.sub('#\+', "", self.raw_message)
            self.message = re.sub(group_notification_regexp, "", self.message)
            self.message = re.sub(add_log_regexp, "", self.message)

            # Notification groups
            self.notification_groups = group_notification_matcher.findall(self.raw_message)

    def __json__(self, request=None):
        json = {
            'message': self.message,
            'application': self.application,
            'level': self.level,
            'date': self.date,
            'tags': self.tags,
            'stack_sha': self.stack_sha,
            '_dt_insert': self._dt_insert
        }
        if self._id is not None:
            json['_id'] = self._id
        return json

    @staticmethod
    def from_bson(bson):
        log = Log(application=bson.get('application'),
                  level=bson.get('level'),
                  message=bson.get('message'),
                  date=jsonizer(bson.get('date')),
                  tags=jsonizer(bson.get('tags')),
                  stack_sha=bson.get('stack_sha'),
                  stack=bson.get('stack'))
        log._id = str(bson.get('_id'))
        log._dt_insert = jsonizer(bson.get('_dt_insert'))
        return log

    @staticmethod
    def init(db):
        db.logs.ensure_index([('date', DESCENDING)])
        db.logs.ensure_index([('date', ASCENDING), ('application', ASCENDING), ('level', ASCENDING)])
        try:
            db.create_collection('tail_logs', capped=True, size=256 * 1024 * 1024)
        except CollectionInvalid:
            pass
        db.tail_logs.ensure_index([('date', ASCENDING)])
        db.tail_logs.ensure_index([('date', ASCENDING), ('application', ASCENDING), ('level', ASCENDING)])

    def save(self, db):
        json_log = self.__json__()
        db.logs.insert(json_log)
        if self.stack is not None:
            json_log['stack'] = self.stack
        db.tail_logs.insert(json_log)


    @staticmethod
    def search(db, dt_since, dt_to, src_query=dict(), page=0, max_result=100, tags=[], sort=[('date', DESCENDING)]):
        if page is None:
            page = 0
        else:
            page = int(page)

        if max_result is None:
            max_result = 100
        else:
            max_result = int(max_result)

        fields = ['message', 'application', 'date', 'level', 'stack_sha', 'tags','_dt_insert']
        # if tags is not None and len(tags) > 0:
        # for tag in tags:
        # fields.append('tags.' + tag)
        # else:

        src_query['date'] = {'$gte': dt_since, '$lte': dt_to}
        _log.debug(src_query)

        for db_log in db.logs.find(src_query, fields=fields, sort=sort, skip=page * max_result, limit=max_result):
            yield Log.from_bson(db_log)


    @staticmethod
    def tail(db, dt_since, dt_to, src_query=dict()):
        src_query['_dt_insert'] = {'$gte': dt_since, '$lte': dt_to}
        _log.debug("log_search:"+str(src_query))
        for db_log in db.logs.find(src_query, sort=[('date', ASCENDING)]):
            yield Log.from_bson(db_log)