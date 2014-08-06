__author__ = 'Igor Maculan <n3wtron@gmail.com>'
from pyramid.view import view_config

from log4all import logger


@view_config(route_name='helper_tags_search', renderer='json', request_method='GET', request_param=['term'])
def helper_tags_search(request):
    result = list()
    logger.debug("term:" + request.GET['term'])
    current_tags = request.GET['term'].split(' ')
    current_tags_cleaned = [t[1:] for t in current_tags]
    partial_tag = current_tags[-1]
    logger.debug("partial_tag:" + partial_tag)
    if len(partial_tag) > 0 and partial_tag[0] == '#':
        src_filter = {
            '$and': [
                {'name': {'$regex': partial_tag[1:]}},
                {'name': {
                    '$not': {'$in': current_tags_cleaned[:-1]}
                }
                }
            ]
        }
        tags = list(
            request.mongodb.tags.find(src_filter, fields={'_id': False, 'date': False})
        )
        str_tags = ""
        for c_tag in current_tags[:-1]:
            str_tags += c_tag + " "
        for tag in tags:
            if '#' + tag['name'] not in str_tags:
                choice = str_tags + '#' + tag['name']
                result.append({'label': choice, 'value': choice})
    return result


@view_config(route_name='helper_application_search', renderer='json', request_method='GET', request_param=['term'])
def helper_application_search(request):
    result = list()
    logger.debug("term:" + request.GET['term'])
    pre_apps = ""
    if 'multi' in request.GET:
        current_apps = request.GET['term'].split(' ')
        partial_app = current_apps[-1]
        for c_app in current_apps[:-1]:
            pre_apps += c_app + " "
        src_filter = {
            '$and': [
                {'name': {'$regex': partial_app}},
                {'name': {
                    '$not': {'$in': current_apps[:-1]}
                }
                }
            ]
        }
    else:
        partial_app = request.GET['term']
        src_filter = {
            'name': {'$regex': partial_app}
        }
    logger.debug("helper_application_search  filter:" + str(src_filter))
    apps = list(request.mongodb.applications.find(src_filter, fields={'name': True}))

    for app in apps:
        result.append({'label': app['name'], 'value': pre_apps + app['name']})
    logger.debug("helper_application_search  result:" + str(result))
    return result