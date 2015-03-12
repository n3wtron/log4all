import logging

from bson import ObjectId
from pyramid.view import view_config
from log4all.api.auth import jwt_secure

from log4all.model.group import Group


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
_log = logging.getLogger(__name__)


@view_config(route_name='api_groups_all', renderer='json', request_method='GET')
@jwt_secure('admin')
def api_groups_all(request):
    return list(Group.search(request.db))


@view_config(route_name='api_group_get', renderer='json', request_method='GET')
def api_group_get(request):
    app = Group.get(request.db, {'_id': ObjectId(request.matchdict['groupId'])})
    return app