import logging

from bson import ObjectId
from pyramid.view import view_config
from log4all.model.user import User


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
_log = logging.getLogger(__name__)


@view_config(route_name='api_users_all', renderer='json', request_method='GET')
def api_users_all(request):
    return list(User.search(request.db))


@view_config(route_name='api_user_get', renderer='json', request_method='GET')
def api_user_get(request):
    app = User.get(request.db, {'_id': ObjectId(request.matchdict['userId'])})
    return app