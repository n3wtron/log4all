import logging

import jwt
from pyramid.response import Response
from pyramid.view import view_config

from log4all.api.auth import auth_secret
from log4all.model.group import Group


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name="api_group_add", renderer='json', request_method="PUT")
def api_group_add(request):


    group = Group(request.json['name'], description=request.json['description'])
    group.save(request.db)
    return {"success": True, 'group': group}