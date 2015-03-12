import logging

import hashlib
import jwt
from pyramid.view import view_config

from log4all.api.auth import auth_secret, _permissions
from log4all.api.util import __new_response
from log4all.model.user import User


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name="api_auth_login", renderer='json', request_method="POST")
def auth_login(request):
    if 'username' not in request.json_body or 'password' not in request.json_body:
        return __new_response({'success': False, 'message': 'username and password parameters are mandatory'},
                              ('Access-Control-Allow-Origin', '*'))
    username = request.json_body['username']
    password = request.json_body['password']
    user = User.get(request.db, {'email': username, 'password': hashlib.md5(password.encode('utf-8')).hexdigest()})
    if user is None:
        return __new_response({'success': False, 'message': 'Authentication error'})
    else:
        token = jwt.encode(user.__dict__, auth_secret)
        return __new_response({'success': True, 'token': token})


@view_config(route_name="api_auth_permissions_list", renderer='json', request_method="GET")
def auth_permissions_list(request):
    return _permissions