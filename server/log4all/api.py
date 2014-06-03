import json
from sqlalchemy import and_, or_
from log4all.models.Log import Log
from log4all.models.LogsTags import LogsTags
from log4all.models.Tag import Tag

__author__ = 'igor'
import logging
from pyramid.view import view_config
import datetime
import time
import re

logger = logging.getLogger('log4all')
hashtag_search_regexp = "#([\\w|.]+)([=|>|<]|>=|<=|!=|~=)([\\w|.]+)"
hashtag_value_regexp = "#([\\w|.]+)(:)([\\w|.]+)"


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
        result['_message'] = re.sub('#', "", raw_log)
        # result['_message'] = re.sub(hashtag_value_regexp, "", raw_log)
        return result
    except Exception as e:
        logger.error(str(e))


def db_insert(request, log):
    if request.registry.settings['db.type'] == 'mongodb':
        log['_date'] = datetime.datetime.now()
        request.mongodb.logs.insert(log)
    else:
        db_log = Log()
        for k in log.keys():
            if k == '_message':
                db_log.message = log[k]
            else:
                # tags
                tag = request.sqldb.query(Tag).filter(Tag.name == k).first()
                if tag is None:
                    # new tag
                    tag = Tag(name=k)
                    request.sqldb.add(tag)
                    request.sqldb.flush()  # to get the autoincrement tag id
                log_tag = LogsTags(log[k])
                log_tag.tag_id = tag.id
                db_log.tags.append(log_tag)
        request.sqldb.add(db_log)


@view_config(route_name='api_logs_add', renderer='json',
             request_method='POST', accept='application/json')
def api_logs_add(request):
    try:
        logger.debug(request.body)
        raw_log = request.json_body['log']
        logger.debug("toAdd:" + raw_log)
        log = parse_raw_log(raw_log)
        db_insert(request, log)
        return {'result': 'success'}
    except Exception as e:
        logger.error(str(e))
        return {'result': 'fail', 'message': str(e)}


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
        logger.error(str(e))


def mongodb_parse_filter(query):
    """
        Query parser for mongodb
    """
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
            if op == '>=':
                mongo_src[src['key']] = {"$gte": src['value']}
            if op == '<=':
                mongo_src[src['key']] = {"$lte": src['value']}

    logger.debug("mongo_src" + str(mongo_src))
    return mongo_src


def sqlalchemy_parse_filter(request, query):
    """
        Query parser for sqlalchemy
    """
    expr_operators, text = parse_hash_expression(query)
    query = request.sqldb.query(Log)
    for op in expr_operators.keys():
        for src in expr_operators[op]:
            if op == '=':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value == src['value'])))
            if op == '~=':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id,
                         LogsTags.value.like('%' + src['value'] + '%'))))
            if op == '!=':
                query = query.filter(or_(
                    Log.tags.any(
                        and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value != src['value'])
                    ),
                    ~Log.tags.any(and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id))))
            if op == '>':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value > int(src['value']))))
            if op == '<':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value < int(src['value']))))
            if op == '>=':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value >= int(src['value']))))
            if op == '<=':
                query = query.filter(Log.tags.any(
                    and_(Tag.name == src['key'], LogsTags.tag_id == Tag.id, LogsTags.value <= int(src['value']))))
    logger.debug("sql query:" + str(query))
    return query


def db_search(request, query, dt_since, dt_to, page=0, result_per_page=10):
    """
        Search method
    """
    result = dict()

    if request.registry.settings['db.type'] == 'mongodb':
        search_filter = mongodb_parse_filter(query)
        search_filter['_date'] = {'$gte': dt_since, '$lte': dt_to}
        logger.debug("Search filter:" + str(search_filter))
        n_rows = request.mongodb.logs.find(search_filter).count()
        result['logs'] = list(
            request.mongodb.logs.find(search_filter, skip=page * result_per_page, limit=result_per_page))
    else:
        # sqlalchemy
        query = sqlalchemy_parse_filter(request, query)
        query = query.filter(Log.dt_insert <= dt_to, Log.dt_insert >= dt_since)
        n_rows = query.count()
        logs = query.slice(page * result_per_page, (page * result_per_page) + result_per_page)

        result['logs'] = []
        for log in logs:
            result['logs'].append(log.as_dict())


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
    # Search
    result = db_search(request, query, dt_since, dt_to, int(page), int(result_per_page))
    # Converting result to json compatible
    for res in result['logs']:
        for key in res.keys():
            if key == '_id':
                res['_id'] = str(res['_id'])
            if isinstance(res[key], datetime.datetime):
                res[key] = res[key].strftime("%Y-%m-%d %H:%M:%S")
    logging.getLogger('log4all').debug(result)
    result['elapsed_time'] = time.time() - start
    return result