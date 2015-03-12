import logging

from hashlib import md5
from pyramid.view import view_config

from log4all import Group
from log4all.model.user import User


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name="api_users_add", renderer='json', request_method="PUT")
def api_user_add(request):
    user = User(request.json['email'], request.json['name'],
                password=md5(request.json['password'].encode('utf-8')).hexdigest(), groups=request.json['groups'])

    user_permissions = set()
    for group in user.groups:
        db_group = Group.get(request.db, {'name': group})
        user_permissions.add(db_group.permissions)
    user.permissions = list(user_permissions)

    user.save(request.db)
    return {"success": True, 'user': user}