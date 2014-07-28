import smtplib
import datetime

from bson import ObjectId
from pyramid.url import route_url
from pyramid.view import view_config

from log4all import logger

from log4all.api.log.search import api_logs_search
from log4all.util import LEVEL_COLORS


@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def detail_view(request):
    try:
        log = request.mongodb.logs.find_one({'_id': ObjectId(request.GET['id'])})
        try:
            stack = request.mongodb.stacks.find_one({'hash_stacktrace': log['_stack_hash']})
        except KeyError:
            stack = None
        logger.debug("Log:" + str(log))
        logger.debug('stack:' + str(stack))
        return {'csrf_token': request.session.get_csrf_token(), 'log': log, 'stack': stack}
    except KeyError:
        return {'error': 'No id parameter found'}


@view_config(route_name='detail_send_notification', renderer='json', request_param=['log_id', 'email', 'csrf'])
def detail_send_notification(request):
    """
    :param request:
        csrf
        log_id
        email
    :return:
        result : True / False
    """
    try:
        logger.debug(str(request.GET))
        if request.GET['csrf'] != request.session.get_csrf_token():
            return {'result': False}
        else:
            smtp_hostname = request.registry.settings['smtp.hostname']
            smtp_port = int(request.registry.settings['smtp.port'])
            from_address = request.registry.settings['smtp.from_address']
            recipient = request.GET['email']
            log_id_detail_url = route_url('detail', request) + "?id=" + request.GET['log_id']
            smtp_server = smtplib.SMTP(smtp_hostname, port=smtp_port)
            content = "From: Log4All <" + from_address + ">\n"
            content += "To: <" + recipient + ">\n"
            content += "MIME-Version: 1.0\n"
            content += "Content-type: text/html\n"
            content += "Subject: log4all notification\n\n"
            content += "<a href=\"" + log_id_detail_url + "\">" + log_id_detail_url + "</a>"
            smtp_server.sendmail(from_address, [recipient], content)
            return {'result': True}
    except Exception as e:
        logger.exception(e)
        return {'result': False}


@view_config(route_name='result_table', renderer='templates/result_table.jinja2', request_method='GET',
             request_param=['query', 'dtSince', 'dtTo'])
def result_table(request):
    result = api_logs_search(request)
    normal_columns = set()
    tag_columns = set()

    for log in result['logs']:
        for nc in log.keys():
            if nc[0] != '_':
                normal_columns.add(nc)
            if nc == '_tags':
                tag_columns.update(log['_tags'].keys())
            if nc == 'date':
                log[nc] = datetime.datetime.fromtimestamp(log[nc]).strftime("%Y-%m-%d %H:%M:%S")
    max_pages = int(result['pages'])

    return {'normal_columns': normal_columns,
            'tag_columns': tag_columns,
            'order': result['order'],
            'curr_page': int(request.GET['page']),
            'result_per_page': int(request.GET['result_per_page']),
            'max_pages': max_pages,
            'n_rows': result['n_rows'],
            'elapsed_time': result['elapsed_time'],
            'logs': result['logs']}


@view_config(route_name='tail_table', renderer='templates/tail_table.jinja2', request_method='GET',
             request_param=['query'])
def tail_table(request):
    logger.debug("query:" + str(request.GET['query']))
    return {
        'level_colors': LEVEL_COLORS,
        'query': str(request.GET['query'])
    }
