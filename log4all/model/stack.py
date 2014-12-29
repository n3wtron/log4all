import logging

import hashlib
from pymongo.errors import DuplicateKeyError

from log4all.util.json_util import jsonizer


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


class Stack:
    def __init__(self, stacktrace=None):
        self.stacktrace = stacktrace
        self.sha = hashlib.sha1(''.join(self.stacktrace).encode('UTF-8')).hexdigest()

    def __json__(self,request=None):
        return jsonizer({
            'sha': self.sha,
            'stacktrace': self.stacktrace
        })

    @staticmethod
    def init(db):
        db.stacktraces.ensure_index('sha', unique=True)

    def save(self, db):
        _log.debug("stack:" + str(self.__json__()) + " inserted")
        try:
            db.stacktraces.insert(self.__json__())
        except DuplicateKeyError as e:
            _log.debug("double stack, no problem")