import logging
import re

from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')

email_checker_re = re.compile('[^@]+@[^@]+\.[^@]+')


def save_user(request, to_add=True):
    err_message = list()
    csrf = request.session.get_csrf_token()
    if csrf != request.POST['csrf']:
        err_message.append('CSRF TOKEN ERROR')

    if 'username' not in request.POST or request.POST['username'].strip() == '':
        err_message.append('Username is mandatory')

    if 'email' not in request.POST or request.POST['email'].strip() == '':
        err_message.append('Email is mandatory')

    if not email_checker_re.match(request.POST['email']):
        err_message.append('Invalid email format')

    user = dict(
        username=request.POST['username'].strip(),
        email=request.POST['email'].strip(),
        name=request.POST['name'].strip(),
        surname=request.POST['surname'].strip(),
        groups=request.POST.getall('groups'),
        notifications=request.POST.getall('notifications')
    )
    if len(err_message) == 0:
        try:
            if to_add:
                request.mongodb.users.insert(user, w=1)
            else:
                request.mongodb.users.update({'username': request.POST['orig_username']}, user, w=1)
        except DuplicateKeyError as e:
            err_message = e.message
    return err_message


def del_user(request):
    err_message = list()
    csrf = request.session.get_csrf_token()
    if csrf != request.POST['csrf']:
        err_message.append('CSRF TOKEN ERROR')

    if 'username' not in request.POST or request.POST['username'].strip() == '':
        err_message.append('Username is mandatory')

    if len(err_message) == 0:
        try:
            request.mongodb.users.remove({'username': request.POST['username'].strip()})
        except DuplicateKeyError as e:
            err_message = e.message

    return err_message


@view_config(route_name='admin_users', renderer='templates/users.jinja2')
def admin_users_view(request):
    error_messages = list()
    if request.method == 'POST' and 'operation' in request.POST:

        if request.POST['operation'] == 'addUser':
            error_messages = save_user(request)
            if len(error_messages) > 0:
                logger.error("Error adding user:" + "".join(error_messages))

        if request.POST['operation'] == 'delUser':
            error_messages = del_user(request)
            if len(error_messages) > 0:
                logger.error("Error deleting user:" + "".join(error_messages))

    users = request.mongodb.users.find().sort([('name', 1)])
    groups = request.mongodb.groups.find({}, {'name': 1}).sort([('name', 1)])
    error_message = ""
    for err in error_messages:
        error_message += err + "</br>"
    return {
        'csrf': request.session.get_csrf_token(),
        'users': users,
        'groups': groups,
        'notif_methods': get_notif_methods(),
        'error_message': error_message
    }


def get_notif_methods():
    return ['email']


@view_config(route_name='admin_edit_user', renderer='templates/user.jinja2', request_param=['user'])
def admin_edit_user_view(request):
    error_message = None
    error_messages = list()
    if request.method == 'POST' and 'operation' in request.POST:
        if request.POST['operation'] == 'updateUser':
            error_messages = save_user(request, False)
            if len(error_messages) > 0:
                logger.error("Error adding user:" + "".join(error_messages))

    for err in error_messages:
        error_message += err + "</br>"

    # prevent error in case of username changed
    if 'username' in request.POST and request.GET['user'] != request.POST['username']:
        target_username = request.POST['username']
    else:
        target_username = request.GET['user']

    user = request.mongodb.users.find_one({'username': target_username})
    if user is None:
        error_message = 'User not found'

    groups = request.mongodb.groups.find({}, {'name': 1}).sort([('name', 1)])
    return {
        'csrf': request.session.get_csrf_token(),
        'error_message': error_message,
        'user': user,
        'groups': groups,
        'notif_methods': get_notif_methods()
    }