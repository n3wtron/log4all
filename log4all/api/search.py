import logging

import re
from pyramid.view import view_config

from log4all import Log
from log4all.api.response import SearchResponse
from log4all.util.regexp import src_key_regexp, value_regexp


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)
operator_regexp = "(=|>|<|>=|<=|!=|\?=|<<|!<)"
search_regexp = src_key_regexp + '(' + operator_regexp + value_regexp + '){0,1}'
search_matcher = re.compile(search_regexp)


def parse_src_expression(raw):
    """
        Parse a string to return a dict[operand] that contain a dict[key|operator|value]
    """
    result = {}
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
                val['key'] = 'tags.' + key[1:]
            else:
                val['key'] = key
            val['operator'] = operator
            if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
                value = value[1:-1]
            val['value'] = value
    return result, search_matcher.sub("", raw)


def mongodb_parse_filter(query):
    """
        Query parser for mongodb
    """
    if query is None:
        return dict()

    expr_operators, text = parse_src_expression(query)
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
    return mongo_src


@view_config(route_name='api_logs_search', renderer='json', request_method="POST")
def api_logs_search(request):
    _log.debug(str(request.json))
    src_query = mongodb_parse_filter(request.json.get('query'))

    src_application = request.json.get('application')
    if src_application is not None:
        src_query['application'] = src_application

    src_levels = request.json.get('levels')
    if src_levels is not None:
        src_query['level'] = {"$in": src_levels}

    response = SearchResponse()

    dt_since = request.json.get('dt_since')
    dt_to = request.json.get('dt_to')
    if dt_since is None or dt_to is None:
        response.success = False
        response.message = 'Since and To are mandatory'
        _log.warn(str(response.json()))
        return response.json()

    _log.debug('src_query:' + str(src_query))
    response.result = list(Log.search(request.db, src_query=src_query,
                                      page=request.json.get('page'),
                                      max_result=request.json.get('max_result'),
                                      tags=request.json.get('tags')))
    return response.json()