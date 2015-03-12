import hashlib

from log4all import Group
from log4all.model.user import User


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
import logging

from bson import ObjectId
from pyramid.view import view_config


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_user_update', renderer='json', request_method='POST')
def api_user_update(request):
    # check if app exist
    db_user = User.get(request.db, {"_id": ObjectId(request.matchdict['userId'])})
    if db_user is None:
        return {'success': False, 'message': 'No user found with id:' + request.json['_id']}
    user = User.from_bson(request.json)
    if db_user.password != request.json['password']:  # password changed
        user.password = hashlib.md5(request.json['password'].encode('utf-8')).hexdigest()
    try:
        if set(db_user.groups) != set(user.groups):
            user_permissions = set()
            for group in user.groups:
                db_group = Group.get(request.db, {'name': group})
                user_permissions = user_permissions.union(db_group.permissions)
            user.permissions = list(user_permissions)
        user.save(request.db)
        return {'success': True}
    except Exception as e:
        _log.exception(e)
        return {'success': False, 'message': str(e)}