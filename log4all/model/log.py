from datetime import datetime
import logging

from pymongo import ASCENDING

import re

from log4all.util.json_util import jsonizer
from log4all.util.regexp import add_log_matcher, add_log_regexp, group_notification_regexp, group_notification_matcher


_log = logging.getLogger(__name__)


class Log:
    def __init__(self, application=None, level=None, raw_message=None, message=None, tags=None,
                 notification_groups=None, stack_sha=None, date=datetime.now()):
        self.application = application
        self.raw_message = raw_message
        self.date = date
        self.level = level
        self.message = message
        self.tags = tags
        self.stack_sha = stack_sha
        self.notification_groups = notification_groups
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

    def json(self):
        return jsonizer({
            'message': self.message,
            'application': self.application,
            'level': self.level,
            'date': self.date,
            'tags': self.tags,
            'stack_sha': self.stack_sha
        })

    @staticmethod
    def init(db):
        db.logs.ensure_index('date')
        db.logs.ensure_index([('date', ASCENDING), ('application', ASCENDING), ('level', ASCENDING)])

    def save(self, db):
        _log.debug("log:" + str(self.json()) + " inserted")
        db.logs.insert(self.json())


    @staticmethod
    def search(db, src_query=dict(), page=0, max_result=100, tags=[]):
        if page is None:
            page = 0
        else:
            page = int(page)

        if max_result is None:
            max_result = 100
        else:
            max_result = int(max_result)

        fields = ['message', 'application', 'date']
        if tags is not None and len(tags)>0:
            for tag in tags:
                fields.append('tags.' + tag)
        else:
            fields.append('tags')

        return db.logs.find(src_query, fields=fields, skip=page * max_result, limit=max_result)