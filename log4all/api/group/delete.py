import logging

from bson import ObjectId
from pyramid.view import view_config

from log4all import User
from log4all.model.group import Group


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_group_delete', renderer='json', request_method='DELETE')
def api_group_delete(request):
    try:
        group = Group.get(request.db, {'_id': ObjectId(request.matchdict['groupId'])})
        for user in User.search(request.db, {'groups': {'$in': [group.name]}}):
            user.groups.remove(group.name)
            user.save(request.db)
        Group.delete(request.db, ObjectId(request.matchdict['groupId']))
        return {'success': True}
    except Exception as e:
        _log.exception(e)
        return {'success': False, 'message': str(e)}