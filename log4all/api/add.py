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
        stack_id = request.mongodb.stacks.insert({'stacktrace': stack})
        log['_stack_id'] = stack_id

    # insert log
    request.mongodb.logs.insert(log)
    request.mongodb.logs.ensure_index('date')

    # update tags collections
    for tag in log['_tags'].keys():
        logger.debug("insert tag:" + tag)
        request.mongodb.tags.insert({'name': tag, 'date': datetime.datetime.now()})
        request.mongodb.tags.ensure_index('name', unique=True)


def parse_raw_stack(raw_stack):
    if raw_stack is None:
        return None
    result = []
    if isinstance(raw_stack, list):
        for line in raw_stack:
            result.append(line)
    return result


@view_config(route_name='api_logs_add', renderer='json',
             request_method='POST', accept='application/json')
def api_logs_add(request):
    try:
        logger.debug(request.body)
        raw_log = request.json_body['log']

        try:
            raw_stack = request.json_body['stack']
        except KeyError:
            raw_stack = None
        stack = parse_raw_stack(raw_stack)

        logger.debug("toAdd: log:" + raw_log + " stack:" + str(raw_stack))
        log = parse_raw_log(raw_log)
        try:
            log['date'] = datetime.datetime.fromtimestamp(long(request.json_body['date'])/1000)
        except KeyError:
            log['date'] = datetime.datetime.now()

        db_insert(request, log, stack)
        return {'result': True}
    except Exception as e:
        logger.error(e.message)
        return {'result': False, 'message': str(e)}
