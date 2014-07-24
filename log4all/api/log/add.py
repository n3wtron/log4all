import hashlib
import logging
import datetime
import re

from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config

from log4all.api.log import hash_regexp, value_regexp


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
add_log_regexp = hash_regexp + "((:)" + value_regexp + "){0,1}"
add_log_matcher = re.compile(add_log_regexp)


def parse_raw_log(raw_log):
    assert isinstance(raw_log, unicode)
    result = dict()
    result['_tags'] = dict()
    raw_tags = add_log_matcher.findall(raw_log)
    for raw_tag in raw_tags:
        tag = raw_tag[0][1:]  # removed '#'
        tag = tag.replace("+", "")
        if len(raw_tag[1]) == 0:
            value = True
        else:
            value = raw_tag[3]
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        result['_tags'][tag] = value
    result['message'] = re.sub('#\+', "", raw_log)
    result['message'] = re.sub(add_log_regexp, "", result['message'])
    return result


def db_insert(db, log, stack=None):
    # add stack if is present
    if stack is not None:
        # prevent duplicated stacktrace documents
        hash_stack = hashlib.sha1(''.join(stack)).hexdigest()
        try:
            db.stacks.insert({'hash_stacktrace': hash_stack, 'stacktrace': stack}, w=1, continue_on_error=True)
        except DuplicateKeyError as e:
            logger.debug("Duplicated stack")
        log['_stack_hash'] = hash_stack

    # insert log
    log_id = db.logs.insert(log)
    tail_log = log
    tail_log['_id'] = log_id
    db.tail_logs.insert(tail_log)

    # update tags collections
    for tag in log['_tags'].keys():
        try:
            db.tags.insert({'name': tag, 'date': datetime.datetime.now()}, w=1)
        except DuplicateKeyError as e:
            logger.debug("Duplicated tags:" + tag)


def parse_raw_stack(raw_stack):
    if raw_stack is None:
        return None
    result = ""
    if isinstance(raw_stack, list):
        for line in raw_stack:
            result += line + '\n'
    return result


def add_log(db, json_log, application):
    if 'level' in json_log:
        level = json_log['level']
    else:
        level = 'INFO'

    raw_log = json_log['log']
    try:
        log_date = datetime.datetime.fromtimestamp(long(json_log['date']) / 1000)
    except KeyError:
        log_date = datetime.datetime.now()
    try:
        raw_stack = json_log['stack']
    except KeyError:
        raw_stack = None

    stack = parse_raw_stack(raw_stack)
    logger.debug("toAdd: log:" + raw_log + " stack:" + str(raw_stack))
    log = parse_raw_log(raw_log)
    log['date'] = log_date
    log['application'] = application['name']
    log['level'] = level
    db_insert(db, log, stack)
    return True, None


@view_config(route_name='api_logs_add', renderer='json',
             request_method='POST', accept='application/json')
def api_logs_add(request):
    logger.debug('Add Log request:' + str(request.json_body))
    success = True
    try:
        logger.debug(request.body)
        err_msg = None
        application = request.json_body['application']
        app = request.mongodb.applications.find_one({'name': application})
        if app is None:
            err_msg = 'Application ' + application + ' not found'
            logger.error(err_msg)
            return {'result': False, 'message': err_msg}

        if 'logs' in request.json_body:
            # Multiple logs to add
            logger.info(str(len(request.json_body['logs'])) + " to add")
            for json_log in request.json_body['logs']:
                add_success, add_err_msg = add_log(request.mongodb, json_log, app)
                if not add_success:
                    err_msg = add_err_msg
                success = success and add_success
        else:
            success, err_msg = add_log(request.mongodb, request.json_body, app)
        return {'result': success, 'message': err_msg}
    except Exception as e:
        logger.error(e.message)
        return {'result': False, 'message': str(e)}
