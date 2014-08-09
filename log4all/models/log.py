from datetime import datetime

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


class Log(object):
    def __init__(self, application, level, date=datetime.now()):
        self.application = application
        self.level = level
        self.date = date
        self.message = None
        self.notification_groups = list()
        self.tags = dict()
