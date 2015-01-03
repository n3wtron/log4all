from datetime import datetime
import logging

from pyramid.view import view_config

from log4all import Tag, Log, Stack


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


def _add_log(application, json_log, db):
    if 'date' in json_log:
        dt_insert = datetime.fromtimestamp(int(json_log['date']) / 1000)
    else:
        dt_insert = datetime.now()
    log = Log(application=application, level=json_log['level'], raw_message=json_log['message'], date=dt_insert)

    # Stack
    if 'stack' in json_log.keys() and json_log['stack'] is not None:
        stack = Stack(stacktrace=json_log['stack'])
        stack.save(db)
        log.stack_sha = stack.sha

    log.save(db)

    # Tags
    if isinstance(log.tags, dict):
        tags = list()
        for tag_name in log.tags.keys():
            tags.append(Tag(tag_name))
        if len(tags) > 0:
            Tag.bulk_save(db, tags)


@view_config(route_name="api_logs_add", request_method="POST", renderer="json")
def api_logs_add(request):
    _log.debug(request.json)
    # check if is a massive log
    try:
        if 'logs' in request.json.keys():
            # multiple log
            for json_log in request.json['logs']:
                _add_log(request.json['application'], json_log, request.db)
        else:
            # single log
            _add_log(request.json['application'], request.json, request.db)
        return {'success': True, 'message': None}
    except Exception as e:
        _log.exception(e)
        return {'success': False, 'message': str(e)}