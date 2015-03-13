import logging

from bson import ObjectId
from pyramid.view import view_config

from log4all import Application


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_application_delete', renderer='json', request_method='DELETE')
def api_application_delete(request):
    Application.delete(request.db, ObjectId(request.matchdict['applicationId']))
    return {'success': True}