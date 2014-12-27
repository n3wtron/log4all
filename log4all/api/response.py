from log4all.util.json_util import jsonizer

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


class SearchResponse:
    def __init__(self, success=True, result=[], message=None):
        self.success = success
        self.result = result
        self.message = message

    def __unicode__(self):
        return self.json()

    def json(self):
        return jsonizer({
            'success':self.success,
            'result' : self.result,
            'message': self.message
        })