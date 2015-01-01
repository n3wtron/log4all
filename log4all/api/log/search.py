from datetime import datetime
import logging

from pymongo import ASCENDING, DESCENDING

import re
from pyramid.view import view_config

from log4all.model.log import Log
from log4all.api.log.response import SearchResponse
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
            if value is not None and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
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
    _log.debug('search request:'+ str(request.json))
    src_query = mongodb_parse_filter(request.json.get('query'))

    src_applications = request.json.get('applications')
    if src_applications is not None:
        if ',' in src_applications:
            # multiple applications
            src_query['application'] = {"$in": [a.strip() for a in src_applications.split(',')]}
        else:
            src_query['application'] = src_applications

    src_levels = request.json.get('levels')
    if src_levels is not None:
        src_query['level'] = {"$in": src_levels}

    src_sort_field = request.json.get('sort_field')
    src_sort_ascending = request.json.get('sort_ascending')
    if src_sort_field is not None and src_sort_ascending is not None:
        sort_direction = ASCENDING if src_sort_ascending else DESCENDING
        sort = [(src_sort_field, sort_direction)]
        _log.debug('sort:' + str(sort))
    response = SearchResponse()

    # Date range
    dt_since_param = request.json.get('dt_since')
    dt_to_param = request.json.get('dt_to')
    if dt_since_param is None or dt_to_param is None:
        response.success = False
        response.message = 'Since and To are mandatory'
        _log.warn(str(response.__json__()))
        return response
    else:
        dt_since = datetime.fromtimestamp(int(dt_since_param)/1000)
        dt_to = datetime.fromtimestamp(int(dt_to_param)/1000)

    _log.debug('src_query:' + str(src_query))

    response.result = list(Log.search(request.db, src_query=src_query,
                                      dt_since=dt_since, dt_to=dt_to,
                                      page=int(request.json.get('page')),
                                      max_result=int(request.json.get('max_result')),
                                      tags=request.json.get('tags'), sort=sort))
    return response

