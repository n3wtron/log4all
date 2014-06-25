from datetime import datetime
import logging

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config

from log4all.util import mongo_db_result_to_json


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')


@view_config(route_name='admin_home', renderer='templates/home.jinja2')
def admin_home(request):
    return {}


@view_config(route_name='admin_applications', renderer='templates/applications.jinja2')
def admin_applications(request):
    return {}


@view_config(route_name="admin_add_application", renderer='json', request_method='POST')
def add_application(request):
    try:
        application_name = request.json_body['name']
        application_description = request.json_body['description']
        application = dict()
        application['name'] = application_name
        application['description'] = application_description
        application['date'] = datetime.now()
        request.mongodb.applications.insert(application, w=1, continue_on_error=False)
        return {'result': True}
    except KeyError as e:
        logger.exception(e)
        return {'result': False, 'message': 'all parameters are mandatory'}
    except DuplicateKeyError as e:
        return {'result': False, 'message': e.message}
    except Exception as e:
        logger.exception(e)
        return {'result': False, 'message': 'error adding application'}


@view_config(route_name="admin_get_applications", renderer='json')
def get_applications(request):
    result = mongo_db_result_to_json(list(request.mongodb.applications.find().sort('name')))
    logger.debug(result)
    return result


def get_level_count(db, application):
    return db.logs.aggregate({'$group': {'_id': "$level", 'count': {'$sum': 1}}})['result']


colors = {'DEBUG': "#99CCCC", 'INFO': '#00CCFF', 'WARN': '#FF9900', 'ERROR': '#FF0000'}


@view_config(route_name="admin_edit_application", renderer='templates/application.jinja2')
def edit_application(request):
    result = dict()
    if request.method == 'POST' and 'csrf' in request.POST and request.POST['csrf'] == request.session.get_csrf_token():
        app = request.mongodb.applications.find_one({'_id': ObjectId(request.POST['idApp'])})
        app['name'] = request.POST['name']
        app['description'] = request.POST['description']
        try:
            request.mongodb.applications.update({'_id': ObjectId(request.POST['idApp'])}, app, w=1)
            result['saved'] = True
        except DuplicateKeyError as e:
            result['error'] = e.message
    else:
        app = request.mongodb.applications.find_one({'_id': ObjectId(request.GET['idApp'])})
    logger.debug('app:' + request.GET['idApp'] + str(app))
    result['csrf'] = request.session.get_csrf_token()
    result['app'] = app
    result['level_stat'] = list()

    for level_stat in get_level_count(request.mongodb, app['_id']):
        result['level_stat'].append({'level': level_stat['_id'], 'value': level_stat['count'], 'color': colors[level_stat['_id']]})
    return result
