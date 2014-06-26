from datetime import datetime
import logging

from bson import ObjectId
from bson.dbref import DBRef
from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config

from log4all.util import mongo_db_result_to_json, LEVEL_COLORS, LEVELS


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
        application_levels = dict()
        application['levels'] = application_levels
        application_levels['DEBUG'] = dict(archive=0, delete=5)
        application_levels['INFO'] = dict(archive=15, delete=30)
        application_levels['WARN'] = dict(archive=30, delete=60)
        application_levels['ERROR'] = dict(archive=90, delete=180)
        application_levels['FATAL'] = dict(archive=180, delete=365)

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
    return db.logs.aggregate([
        {'$match': {'application': DBRef('applications', application)}},
        {'$group': {'_id': "$level", 'count': {'$sum': 1}}},
    ])['result']


@view_config(route_name="admin_edit_application", renderer='templates/application.jinja2')
def edit_application(request):
    result = dict()
    if request.method == 'POST' and 'csrf' in request.POST and request.POST['csrf'] == request.session.get_csrf_token():
        # Modification from Form
        app = request.mongodb.applications.find_one({'_id': ObjectId(request.POST['idApp'])})
        app['name'] = request.POST['name']
        app['description'] = request.POST['description']

        try:
            for post_param in request.POST.keys():
                if post_param.endswith('_delete') or post_param.endswith('_archive'):
                    part = post_param.split('_')
                    level = part[0]
                    param_type = part[1]
                    if request.POST[post_param].strip() != '':
                        app['levels'][level][param_type] = int(request.POST[post_param])

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
    result['levels'] = LEVELS
    for level_stat in get_level_count(request.mongodb, app['_id']):
        result['level_stat'].append(
            {'level': level_stat['_id'],
             'value': level_stat['count'],
             'color': LEVEL_COLORS[level_stat['_id']]}
        )
    return result
