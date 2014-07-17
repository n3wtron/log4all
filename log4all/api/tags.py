import logging
from pyramid.view import view_config

__author__ = 'Igor Maculan <n3wtron@gmail.com>'
logger = logging.getLogger('log4all')

@view_config(route_name='api_tags_list', renderer='json', request_method='GET')
def api_tags_list(request):
    result = list(request.mongodb.tags.find({},fields={'_id': False, 'date': False}))
    logger.debug(str(result))
    return result