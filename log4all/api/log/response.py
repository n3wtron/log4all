from log4all.util.json_util import jsonizer

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


class SearchResponse:
    def __init__(self, success=True, result=[], message=None):
        self.success = success
        self.result = result
        self.message = message

    def __unicode__(self):
        return self.__json__()

    def __json__(self, request=None):
        return {
            'success':self.success,
            'result' : self.result,
            'message': self.message
        }