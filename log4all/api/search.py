from log4all.api import hash_regexp, value_regexp
import logging
from pyramid.view import view_config
import datetime
import time
import re

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
hashtag_search_regexp = hash_regexp + "([=|>|<]|>=|<=|!=|~=)" + value_regexp


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
                    mongo_src['tags.' + src['key']] = src['value']
                if op == '~=':
                    mongo_src['tags.' + src['key']] = {'$regex': src['value']}
                if op == '!=':
                    mongo_src['tags.' + src['key']] = {"$ne": src['value']}
                if op == '>':
                    mongo_src['tags.' + src['key']] = {"$gt": src['value']}
                if op == '<':
                    mongo_src['tags.' + src['key']] = {"$lt": src['value']}
                if op == '>=':
                    mongo_src['tags.' + src['key']] = {"$gte": src['value']}
                if op == '<=':
                    mongo_src['tags.' + src['key']] = {"$lte": src['value']}
        logger.debug("mongo_src" + str(mongo_src))
    return mongo_src


def db_search(request, query, dt_since, dt_to, order, page=0, result_per_page=10):
    """
        Search method
    """
    result = dict()
    search_filter = mongodb_parse_filter(query)
    search_filter['date'] = {'$gte': dt_since, '$lte': dt_to}
    logger.debug("Search filter:" + str(search_filter))
    n_rows = request.mongodb.logs.find(search_filter).count()
    sort_param = (order['column'], -1 if order['ascending'] else 1)

    logger.debug("sort_param:" + str(sort_param))
    qry_result = list(
        request.mongodb.logs.find(search_filter, fields=['date', 'message', '_stack_id', 'tags'],
                                  skip=page * result_per_page,
                                  limit=result_per_page).sort([sort_param]))
    result['logs'] = list()
    for row in qry_result:
        try:
            row['_stack_id'] = str(row['_stack_id'])
        except KeyError:
            pass
        result['logs'].append(row)

    result['n_rows'] = n_rows
    result['pages'] = (n_rows / result_per_page) + (n_rows % result_per_page != 0) if 1 else 0
    return result


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
    # Converting result to json compatible
    for res in result['logs']:
        for key in res.keys():
            if key == '_id':
                res['_id'] = str(res['_id'])
            if isinstance(res[key], datetime.datetime):
                res[key] = res[key].strftime("%Y-%m-%d %H:%M:%S")
    result['elapsed_time'] = time.time() - start
    result['order'] = order
    return result
