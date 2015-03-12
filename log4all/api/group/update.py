from log4all import User
from log4all.model.group import Group

__author__ = 'Igor Maculan <n3wtron@gmail.com>'
import logging

from bson import ObjectId
from pyramid.view import view_config


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_group_update', renderer='json', request_method='POST')
def api_group_update(request):
    # check if app exist
    db_group = Group.get(request.db, {"_id": ObjectId(request.matchdict['groupId'])})
    if db_group is None:
        return {'success': False, 'message': 'No group found with id:' + request.json['_id']}

    group = Group.from_bson(request.json)
    # check if the group permissions are changed
    db_permissions = list()
    new_permissions = list()
    try:
        db_permissions = list(db_group.permissions)
    except TypeError:
        pass
    try:
        new_permissions = list(group.permissions)
    except TypeError:
        pass
    try:
        group.save(request.db)
        if set(db_permissions) != set(new_permissions) or db_group.name != group.name:
            # change permissions of related users
            users = User.search(request.db, {'groups': {'$in': [group.name]}})
            for user in users:
                user.permissions = new_permissions
                if db_group.name != group.name:
                    user.groups.remove(db_group.name)
                    user.groups.append(group.name)
                user.save(request.db)
        return {'success': True}
    except Exception as e:
        _log.exception(e)
        return {'success': False, 'message': str(e)}