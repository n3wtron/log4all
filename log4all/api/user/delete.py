import logging

from bson import ObjectId
from pyramid.view import view_config

from log4all.model.user import User


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_user_delete', renderer='json', request_method='DELETE')
def api_user_delete(request):
    User.delete(request.db, ObjectId(request.matchdict['userId']))
    return {'success': True}