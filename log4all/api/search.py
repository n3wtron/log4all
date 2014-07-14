import logging
import datetime
import time
import re

from bson.dbref import DBRef
from bson.objectid import ObjectId
from pyramid.view import view_config

from log4all.api import hash_regexp, value_regexp


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
operator_regexp = "([=|>|<]|>=|<=|!=|~=)"
hashtag_search_regexp = hash_regexp + '(' + operator_regexp + value_regexp + '){0,1}'


def parse_hash_expression(raw):
    """
        Parse a string to return a dict[operand] that contain a dict[key|operator|value]
    """
    assert isinstance(raw, unicode)
    result = {}
    try:
        matcher = re.compile(hashtag_search_regexp)
        raw_tags = matcher.findall(raw)
        for raw_tag in raw_tags:
            tag = raw_tag[0]
            if len(raw_tag[1]) == 0:
                # check if tag exist
                operator = '#'
                value = None
            else:
                # tag with value
                operator = raw_tag[2]
                value = raw_tag[3]

            if not operator in result:
                result[operator] = list()
            val = dict()
            result[operator].append(val)
            val['key'] = tag
            val['operator'] = operator
            val['value'] = value
        return result, matcher.sub("", raw)
    except Exception as e:
        logger.exception(e)


def mongodb_parse_filter(query):
    """
        Query parser for mongodb
    """
    expr_operators, text = parse_hash_expression(query)
    logger.debug("expr_operators:" + str(expr_operators))
    mongo_src = dict()
    if len(expr_operators) > 0:
        for op in expr_operators.keys():
            for src in expr_operators[op]:
                if op == '=':
                    mongo_src['_tags.' + src['key']] = src['value']
                if op == '~=':
                    mongo_src['_tags.' + src['key']] = {'$regex': src['value']}
                if op == '!=':
                    mongo_src['_tags.' + src['key']] = {"$ne": src['value']}
                if op == '>':
                    mongo_src['_tags.' + src['key']] = {"$gt": src['value']}
                if op == '<':
                    mongo_src['_tags.' + src['key']] = {"$lt": src['value']}
                if op == '>=':
                    mongo_src['_tags.' + src['key']] = {"$gte": src['value']}
                if op == '<=':
                    mongo_src['_tags.' + src['key']] = {"$lte": src['value']}
                if op == '#':
                    mongo_src['_tags.' + src['key']] = {"$exists": True}
        logger.debug("mongo_src" + str(mongo_src))
    return mongo_src


def db_search(request, query, dt_since, dt_to, order, page=None, result_per_page=None):
    """
        Search method
    """
    result = dict()
    search_filter = mongodb_parse_filter(query)
    search_filter['date'] = {'$gte': dt_since, '$lte': dt_to}
    logger.debug("Search filter:" + str(search_filter))
    n_rows = request.mongodb.logs.find(search_filter).count()
    sort_param = (order['column'], 1 if order['ascending'] else -1)

    logger.debug("sort_param:" + str(sort_param))

    if page is not None and result_per_page is not None:
        cursor = request.mongodb.logs.find(search_filter,
                                           fields=['date', 'level', 'application', 'message', '_stack_id', '_tags'],
                                           skip=page * result_per_page,
                                           limit=result_per_page).sort([sort_param])
    else:
        cursor = request.mongodb.tail_logs.find(search_filter,
                                                fields=['date', 'level', 'application', 'message', '_stack_id',
                                                        '_tags'])
        cursor.sort([sort_param])
    result['logs'] = list(cursor)
    result['n_rows'] = n_rows
    if page is not None and result_per_page is not None:
        result['pages'] = (n_rows / result_per_page) + (n_rows % result_per_page != 0) if 1 else 0
    return result


def adjust_result(db, result):
    # Converting result to json compatible
    for res in result['logs']:
        for key in res.keys():
            if key == '_id' or key == '_stack_id':
                res[key] = str(res[key])
            if isinstance(res[key], datetime.datetime):
                res[key] = time.mktime(res[key].timetuple())


@view_config(route_name='api_logs_search', renderer='json', request_method='GET',
             request_param=['query', 'dtSince', 'dtTo'])
def api_logs_search(request):
    start = time.time()
    logger.debug(str(request.GET))
    query = request.GET['query']
    dt_since_str = request.GET['dtSince']
    dt_to_str = request.GET['dtTo']
    page = request.GET['page']

    result_per_page = request.GET['result_per_page']
    dt_since = None
    dt_to = None
    if dt_since_str.strip() != '' and dt_to_str.strip() != '':
        dt_since = datetime.datetime.fromtimestamp(int(dt_since_str))
        dt_to = datetime.datetime.fromtimestamp(int(dt_to_str))

    # Order
    order = dict()
    order['column'] = request.GET['order[column]']
    order['ascending'] = True if request.GET['order[ascending]'] == 'true' else False
    logger.debug("order:" + str(order))

    # Search
    result = db_search(request, query, dt_since, dt_to, order, int(page), int(result_per_page))
    adjust_result(request.mongodb, result)
    result['elapsed_time'] = time.time() - start
    result['order'] = order
    return result


@view_config(route_name='api_logs_tail', renderer='json', request_method='GET',
             request_param=['query', 'dtSince'])
def api_logs_tail(request):
    logger.debug("api_logs_tail")
    query = request.GET['query']
    dt_since_str = request.GET['dtSince']
    dt_since = datetime.datetime.fromtimestamp(int(dt_since_str))

    # Order
    order = {'column': 'date', 'ascending': True}

    result = db_search(request, query, dt_since, datetime.datetime.now(), order)
    adjust_result(request.mongodb, result)

    logger.debug("tail n_result:" + str(result['n_rows']))
    return result