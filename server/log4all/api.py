__author__ = 'igor'
import logging
from pyramid.view import view_config
import datetime

import re

logger = logging.getLogger('log4all')
hashtag_search_regexp = "#(\\w+)([=|>|<]|!=|~=)(\\w+)"
hashtag_value_regexp = "#(\\w+)(:)(\\w+)"


def parse_raw_log(raw_log):
    assert isinstance(raw_log, unicode)
    result = {}
    try:
        matcher = re.compile(hashtag_value_regexp)
        raw_tags = matcher.findall(raw_log)
        for raw_tag in raw_tags:
            tag = raw_tag[0]
            value = raw_tag[2]
            result[tag] = value
        result['message'] = re.sub(hashtag_value_regexp, "", raw_log)
        return result
    except Exception as e:
        logger.error(str(e))


@view_config(route_name='api_logs_add', renderer='json',
             request_method='POST', accept='application/x-www-form-urlencoded')
def api_logs_add(request):
    try:
        raw_log = request.POST['log']
        logger.debug("toAdd:" + raw_log)
        log = parse_raw_log(raw_log)
        if log.get('date') is None:
            log['date'] = datetime.datetime.now()
        request.db.logs.insert(log)
        return {'result': 'success'}
    except Exception as e:
        logger.error(str(e))
        return {'result': 'fail', 'message': str(e)}


def parse_hash_expression(raw):
    assert isinstance(raw, unicode)
    result = {}
    try:
        matcher = re.compile(hashtag_search_regexp)
        raw_tags = matcher.findall(raw)
        for raw_tag in raw_tags:
            operator = raw_tag[1]
            if not operator in result:
                result[operator] = []
            val = {}
            result[operator].append(val)
            val['key'] = raw_tag[0]
            val['operator'] = operator
            val['value'] = raw_tag[2]
        return result, matcher.sub("", raw)
    except Exception as e:
        logger.error(str(e))


def parse_filter(query):
    expr_operators, text = parse_hash_expression(query)
    logger.debug("expr_operators:" + str(expr_operators))
    mongo_src = {}
    for op in expr_operators.keys():
        for src in expr_operators[op]:
            if op == '=':
                mongo_src[src['key']] = src['value']
            if op == '~=':
                mongo_src[src['key']] = {'$regex': src['value']}
            if op == '!=':
                mongo_src[src['key']] = {"$ne": src['value']}
            if op == '>':
                mongo_src[src['key']] = {"$gt": src['value']}
            if op == '<':
                mongo_src[src['key']] = {"$lt": src['value']}
    logger.debug("mongo_src" + str(mongo_src))
    return mongo_src


@view_config(route_name='api_logs_search', renderer='json', request_method='GET',
             request_param=['query', 'dtSince', 'dtTo'])
def api_logs_search(request):
    logger.debug(str(request.GET))
    search_filter = parse_filter(request.GET['query'])
    dt_since_str = request.GET['dtSince']
    dt_to_str = request.GET['dtTo']
    if dt_since_str.strip() != '' and dt_to_str.strip() != '':
        dt_since = datetime.datetime.fromtimestamp(int(dt_since_str))
        dt_to = datetime.datetime.fromtimestamp(int(dt_to_str))
        search_filter['date'] = {'$gte': dt_since, '$lte': dt_to}
    logger.debug("Search filter:" + str(search_filter))
    # Search
    result = list(request.db.logs.find(search_filter))
    for res in result:
        for key in res.keys():
            if key == '_id':
                res['_id'] = str(res['_id'])
            if isinstance(res[key], datetime.datetime):
                res[key] = res[key].strftime("%Y-%m-%d %H:%M:%S")
    logging.getLogger('log4all').debug(result)
    return result