import hashlib
from log4all.api import hash_regexp, value_regexp
import logging
from pyramid.view import view_config
import datetime
import re

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
add_log_regexp = hash_regexp + "((:)" + value_regexp + "){0,1}"


def parse_raw_log(raw_log):
    assert isinstance(raw_log, unicode)
    result = dict()
    result['_tags'] = dict()
    matcher = re.compile(add_log_regexp)
    raw_tags = matcher.findall(raw_log)
    for raw_tag in raw_tags:
        tag = raw_tag[0].replace("+", "")
        if len(raw_tag[1]) == 0:
            value = True
        else:
            value = raw_tag[3]
        result['_tags'][tag] = value
    result['message'] = re.sub('#\+', "", raw_log)
    result['message'] = re.sub(add_log_regexp, "", result['message'])
    return result


def db_insert(request, log, stack=None):
    # add stack if is present
    if stack is not None:
        #prevent multiple stacktrace documents
        hash_stack = hashlib.sha1(''.join(stack)).hexdigest()
        db_stack = request.mongodb.stacks.find_one({'hash_stacktrace': hash_stack})
        if db_stack:
            log['_stack_id'] = db_stack['_id']
        else:
            stack_id = request.mongodb.stacks.insert({'hash_stacktrace': hash_stack, 'stacktrace': stack})
            log['_stack_id'] = stack_id

    # insert log
    request.mongodb.logs.insert(log)

    # update tags collections
    for tag in log['_tags'].keys():
        request.mongodb.tags.insert({'name': tag, 'date': datetime.datetime.now()})


def parse_raw_stack(raw_stack):
    if raw_stack is None:
        return None
    result = []
    if isinstance(raw_stack, list):
        for line in raw_stack:
            result.append(line)
    return result


def add_log(request, json_log):
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

    db_insert(request, log, stack)
    return True


@view_config(route_name='api_logs_add', renderer='json',
             request_method='POST', accept='application/json')
def api_logs_add(request):
    success = True
    try:
        logger.debug(request.body)
        if 'logs' in request.json_body:
            logger.info(str(len(request.json_body['logs']))+" to add")
            for json_log in request.json_body['logs']:
                success = success and add_log(request, json_log)
        else:
            success = add_log(request, request.json_body)
        return {'result': success}
    except Exception as e:
        logger.error(e.message)
        return {'result': False, 'message': str(e)}
