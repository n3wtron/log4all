import logging
import smtplib
from bson import ObjectId
from pyramid.url import route_url
from pyramid.view import view_config

logger = logging.getLogger('log4all')


@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def detail_view(request):
    try:
        log = request.mongodb.logs.find_one({'_id': ObjectId(request.GET['id'])})
        try:
            stack = request.mongodb.stacks.find_one({'_id': log['stack_id']})
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


@view_config(route_name='api_tags_search', renderer='json', request_method='GET', request_param=['term'])
def api_tags_search(request):
    result = list()
    logger.debug("term:" + request.GET['term'])
    current_tags = request.GET['term'].split(' ')
    partial_tag = current_tags[-1]
    logger.debug("partial_tag:" + partial_tag)
    if partial_tag[0] == '#':
        tags = list(
            request.mongodb.tags.find({'name': {'$regex': partial_tag[1:]}}, fields={'_id': False, '_date': False}))
        str_tags = ""
        for c_tag in current_tags[:-1]:
            str_tags += c_tag + " "
        for tag in tags:
            if '#'+tag['name'] not in str_tags:
                choice = str_tags + '#'+tag['name']
                result.append({'label': choice, 'value': choice})
    return result