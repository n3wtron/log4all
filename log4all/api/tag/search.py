from pyramid.view import view_config
from log4all import Tag

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


@view_config(route_name='api_tags_get', renderer='json', request_method='GET')
def api_application_get(request):
    tags = list(Tag.search(request.db, {}))
    return tags