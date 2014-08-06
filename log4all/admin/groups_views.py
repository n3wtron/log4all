import logging

from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config

from log4all.util import LEVELS


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger(__name__)


def save_group(request, to_add=True):
    err_message = list()
    csrf = request.session.get_csrf_token()
    if csrf != request.POST['csrf']:
        err_message.append('CSRF TOKEN ERROR')

    if 'name' not in request.POST or request.POST['name'].strip() == '':
        err_message.append('Group name is mandatory')

    group = dict(
        name=request.POST['name'],
        description=request.POST['description'],
        notification_levels=request.POST.getall('notification_levels')
    )

    if len(err_message) == 0:
        try:
            if to_add:
                request.mongodb.groups.insert(group)
            else:
                orig_name = request.POST['original_name']
                request.mongodb.groups.update({'name': orig_name}, group)
                if group['name'] != orig_name:
                    request.mongodb.users.update({'groups': orig_name}, {'$push': {'groups': group['name']}},
                                                 multi=True)
                    request.mongodb.users.update({'groups': orig_name}, {'$pull': {'groups': orig_name}}, multi=True)
        except DuplicateKeyError as e:
            logger.exception(e)
            err_message = e.message
    return err_message


def del_group(request):
    err_message = list()
    csrf = request.session.get_csrf_token()
    if csrf != request.POST['csrf']:
        err_message.append('CSRF TOKEN ERROR')

    if 'name' not in request.POST or request.POST['name'].strip() == '':
        err_message.append('Group name is mandatory')

    if len(err_message) == 0:
        try:
            group_name = request.POST['name'].strip()
            request.mongodb.groups.remove({'name': group_name})
            request.mongodb.users.update({'groups': group_name}, {'$pull': {'groups': group_name}}, multi=True)
        except DuplicateKeyError as e:
            err_message = e.message

    return err_message


@view_config(route_name='admin_groups', renderer='templates/groups.jinja2')
def admin_groups_view(request):
    error_messages = list()
    if request.method == 'POST' and 'operation' in request.POST:
        if request.POST['operation'] == 'addGroup':
            error_messages = save_group(request)
            if len(error_messages) > 0:
                logger.error("Error adding user:" + "".join(error_messages))
        if request.POST['operation'] == 'delGroup':
            error_messages = del_group(request)
            if len(error_messages) > 0:
                logger.error("Error deleting user:" + "".join(error_messages))

    groups = request.mongodb.groups.find().sort([('name', 1)])

    error_message = ""
    for err in error_messages:
        error_message += err + "</br>"

    return {
        'csrf': request.session.get_csrf_token(),
        'groups': groups,
        'error_message': error_message,
        'levels': LEVELS
    }


@view_config(route_name='admin_edit_group', renderer='templates/group.jinja2', request_param=['group'])
def admin_edit_group_view(request):
    error_messages = list()
    if request.method == 'POST' and 'operation' in request.POST:
        if request.POST['operation'] == 'updateGroup':
            error_messages = save_group(request, False)
            if len(error_messages) > 0:
                logger.error("Error adding user:" + "".join(error_messages))

    if 'name' in request.POST:
        group = request.POST['name']
    else:
        group = request.GET['group']

    group = request.mongodb.groups.find_one({'name': group})

    error_message = ""
    for err in error_messages:
        error_message += err + "</br>"

    return {
        'csrf': request.session.get_csrf_token(),
        'group': group,
        'error_message': error_message,
        'levels': LEVELS
    }