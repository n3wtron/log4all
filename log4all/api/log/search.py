import logging
import datetime
import time
import re

from pyramid.view import view_config

from log4all.api.log import value_regexp, src_key_regexp


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')
operator_regexp = "(=|>|<|>=|<=|!=|\?=|<<|!<)"
search_regexp = src_key_regexp + '(' + operator_regexp + value_regexp + '){0,1}'
search_matcher = re.compile(search_regexp)


def parse_src_expression(raw):
    """
        Parse a string to return a dict[operand] that contain a dict[key|operator|value]
    """
    assert isinstance(raw, unicode)
    result = {}
    try:
        raw_exprs = search_matcher.findall(raw)
        for raw_expr in raw_exprs:
            key = raw_expr[0]
            operator = None
            if len(raw_expr[1]) == 0:
                if key[0] == '#':
                    # check if tag exist
                    operator = '#'
                    value = None
            else:
                # tag with value
                operator = raw_expr[2]
                value = raw_expr[3]
            if operator is not None:
                if not operator in result:
                    result[operator] = list()
                val = dict()
                result[operator].append(val)
                if key[0] == '#':
                    val['key'] = '_tags.' + key[1:]
                else:
                    val['key'] = key
                val['operator'] = operator
                if ( value[0] == '"' and value[-1] == '"' ) or ( value[0] == "'" and value[-1] == "'" ):
                    value = value[1:-1]
                val['value'] = value
        return result, search_matcher.sub("", raw)
    except Exception as e:
        logger.exception(e)


def mongodb_parse_filter(query):
    """
        Query parser for mongodb
    """
    expr_operators, text = parse_src_expression(query)
    logger.debug("expr_operators:" + str(expr_operators))
    mongo_src = dict()
    if len(expr_operators) > 0:
        for op in expr_operators.keys():
            for src in expr_operators[op]:
                if op == '=':
                    mongo_src[src['key']] = src['value']
                if op == '?=':
                    mongo_src[src['key']] = {'$regex': src['value']}
                if op == '!=':
                    mongo_src[src['key']] = {"$ne": src['value']}
                if op == '<<':
                    mongo_src[src['key']] = {"$in": src['value'].split(',')}
                if op == '!<':
                    mongo_src[src['key']] = {"$not": {"$in": src['value'].split(',')}}
                if op == '>':
                    mongo_src[src['key']] = {"$gt": src['value']}
                if op == '<':
                    mongo_src[src['key']] = {"$lt": src['value']}
                if op == '>=':
                    mongo_src[src['key']] = {"$gte": src['value']}
                if op == '<=':
                    mongo_src[src['key']] = {"$lte": src['value']}
                if op == '#':
                    mongo_src[src['key']] = {"$exists": True}
        logger.debug("mongo_src" + str(mongo_src))
    return mongo_src


def db_search(request, query, dt_since, dt_to, order, page=None, result_per_page=None, result_columns=None):
    """
        Search method
    """
    if result_columns is None:
        result_attributes = ['date', 'level', 'application', 'message', '_stack_hash', '_tags']
    else:
        result_attributes = list()
        for res_col in result_columns:
            if res_col.strip() != '':
                if res_col[0] == '#':
                    result_attributes.append('_tags.' + res_col[1:])
                else:
                    result_attributes.append(res_col)

    result = dict()
    search_filter = mongodb_parse_filter(query)
    search_filter['date'] = {'$gte': dt_since, '$lte': dt_to}
    logger.debug("Search filter:" + str(search_filter))
    n_rows = request.mongodb.logs.find(search_filter).count()
    sort_param = (order['column'], 1 if order['ascending'] else -1)

    logger.debug("sort_param:" + str(sort_param))

    if page is not None and result_per_page is not None:
        cursor = request.mongodb.logs.find(search_filter,
                                           fields=result_attributes,
                                           skip=page * result_per_page,
                                           limit=result_per_page).sort([sort_param])
    else:
        # Tail
        cursor = request.mongodb.tail_logs.find(search_filter)
        cursor.sort([sort_param])
    result['logs'] = list(cursor)
    result['n_rows'] = n_rows
    if page is not None and result_per_page is not None:
        result['pages'] = (n_rows / result_per_page) + (n_rows % result_per_page != 0) if 1 else 0
    return result


def adjust_result(db, result, full_log=False):
    # Converting result to json compatible
    for res in result['logs']:
        for key in res.keys():
            if key == '_id' or key == '_stack_id':
                res[key] = str(res[key])
            if isinstance(res[key], datetime.datetime):
                res[key] = time.mktime(res[key].timetuple())
            if key == '_stack_hash' and full_log:
                res['stacktrace'] = db.stacks.find_one({'hash_stacktrace': res['_stack_hash']},
                                                       fields=['stacktrace'])
                if res['stacktrace'] and 'stacktrace' in res['stacktrace']:
                    res['stacktrace'] = res['stacktrace']['stacktrace']


@view_config(route_name='api_logs_search', renderer='json', request_method='GET',
             request_param=['query', 'dtSince', 'dtTo'])
def api_logs_search(request):
    start = time.time()
    logger.debug(str(request.GET))
    query = request.GET['query']
    dt_since_str = request.GET['dtSince']
    dt_to_str = request.GET['dtTo']
    if 'page' in request.GET:
        page = request.GET['page']
    else:
        page = 0
    result_columns = None
    if 'columns' in request.GET and request.GET['columns'].strip() != '':
        logger.debug("column:" + str(request.GET['columns']))
        result_columns = request.GET['columns'].split(',')

    if 'result_per_page' in request.GET:
        result_per_page = request.GET['result_per_page']
    else:
        result_per_page = 10

    dt_since = None
    dt_to = None
    if dt_since_str.strip() != '' and dt_to_str.strip() != '':
        dt_since = datetime.datetime.fromtimestamp(int(dt_since_str))
        dt_to = datetime.datetime.fromtimestamp(int(dt_to_str))

    # Order
    order = dict()
    if 'order[column]' in request.GET and 'order[ascending]' in request.GET:
        order['column'] = request.GET['order[column]']
        order['ascending'] = True if request.GET['order[ascending]'] == 'true' else False
    else:
        order['column'] = 'date'
        order['ascending'] = True

    logger.debug("order:" + str(order))

    # Search
    result = db_search(request, query, dt_since, dt_to, order, int(page), int(result_per_page),
                       result_columns=result_columns)

    full_log = True if 'full' in request.GET and request.GET['full'].lower() == 'true' else False

    adjust_result(request.mongodb, result, full_log)
    result['elapsed_time'] = time.time() - start
    result['order'] = order
    return result


@view_config(route_name='api_logs_tail', renderer='json', request_method='GET',
             request_param=['query', 'dtSince'])
def api_logs_tail(request):
    logger.debug("api_logs_tail")
    query = request.GET['query']
    dt_since_str = request.GET['dtSince']
    result_columns = None
    if 'columns' in request.GET and request.GET['columns'].strip() != '':
        logger.debug("column:" + str(request.GET['columns']))
        result_columns = request.GET['columns'].split(',')
    dt_since = datetime.datetime.fromtimestamp(int(dt_since_str))

    # Order
    order = {'column': 'date', 'ascending': True}

    result = db_search(request, query, dt_since, datetime.datetime.now(), order, result_columns=result_columns)
    full_log = True if 'full' in request.GET and request.GET['full'].lower() == 'true' else False
    adjust_result(request.mongodb, result)

    logger.debug("tail n_result:" + str(result['n_rows']))
    return result