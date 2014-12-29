import logging
from bson import ObjectId

from pyramid.view import view_config

from log4all import Application


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
_log = logging.getLogger(__name__)


@view_config(route_name='api_applications_all', renderer='json', request_method='GET')
def api_applications_all(request):
    return list(Application.search(request.db))


@view_config(route_name='api_application_get', renderer='json', request_method='GET')
def api_application_get(request):
    app = Application.get(request.db, {'_id': ObjectId(request.params['id'])})
    return app