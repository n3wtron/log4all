from log4all.api import hash_regexp, value_regexp
from log4all.models.Log import Log
from log4all.models.LogsTags import LogsTags
from log4all.models.Tag import Tag
import logging
from pyramid.view import view_config
import datetime
import re

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
add_log_regexp = hash_regexp + "(:)" + value_regexp


def parse_raw_log(raw_log):
    assert isinstance(raw_log, unicode)
    result = dict()
    result['tags'] = dict()
    try:
        matcher = re.compile(add_log_regexp)
        raw_tags = matcher.findall(raw_log)
        for raw_tag in raw_tags:
            tag = raw_tag[0].replace("+", "")
            value = raw_tag[2]
            result['tags'][tag] = value
        result['_message'] = re.sub('#\+', "", raw_log)
        result['_message'] = re.sub(add_log_regexp, "", result['_message'])
        return result
    except Exception as e:
        logger.exception(e)


def db_insert(request, log, stack=None):
    # add stack if is present
    if stack is not None:
        stack_id = request.mongodb.stacks.insert({'stacktrace': stack})
        log['stack_id'] = stack_id
    if '_date' not in log.keys():
        log['_date'] = datetime.datetime.now()
    # insert log
    request.mongodb.logs.insert(log)
    # update tags collections
    for tag in log['tags'].keys():
        logger.debug("insert tag:" + tag)
        request.mongodb.tags.insert({'name': tag, '_date': datetime.datetime.now()})
        request.mongodb.tags.create_index('name', unique=True)


def parse_raw_stack(raw_stack):
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

        logger.debug("toAdd: log:" + raw_log + " stack:" + str(raw_stack))
        log = parse_raw_log(raw_log)
        stack = parse_raw_stack(raw_stack)
        db_insert(request, log, stack)
        return {'result': True}
    except Exception as e:
        logger.error(e.message)
        return {'result': False, 'message': str(e)}
