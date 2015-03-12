import logging

import jwt
from jwt.exceptions import DecodeError
from pyramid.response import Response


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
_log = logging.getLogger(__name__)


auth_secret = "9400d5b2-072d-4e8d-9ca4-5e9ebe02aad0"

_permissions = ['admin']


def _not_autorized():
    not_authorized_resp = Response()
    not_authorized_resp.status = 401
    return not_authorized_resp


def jwt_secure(permissions):
    """
    Decorator to check permission with JWT header
    :param permissions: list of necessary permissions
    """
    if isinstance(permissions, str):
        lst_permission = [permissions]
    else:
        lst_permission = permissions

    def jwt_decorator(fun):
        def fun_wrapper(request):
            if request.authorization is None:
                return _not_autorized()
            else:
                _log.debug(request.authorization)
                try:
                    secure_data = jwt.decode(request.authorization[1], auth_secret)
                    _log.debug(secure_data)
                    if 'permissions' not in secure_data or \
                            not isinstance(secure_data['permissions'], list) or \
                            not set(secure_data['permissions']).issuperset(set(lst_permission)):
                        return _not_autorized()
                    return fun(request)
                except DecodeError as e:
                    _log.exception(e)
                    return _not_autorized()

        return fun_wrapper

    return jwt_decorator