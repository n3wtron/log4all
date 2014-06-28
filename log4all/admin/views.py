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


def _init_applications_levels(app):
    application_levels = dict()
    app['levels'] = application_levels
    application_levels['DEBUG'] = dict()
    application_levels['INFO'] = dict()
    application_levels['WARN'] = dict()
    application_levels['ERROR'] = dict()
    application_levels['FATAL'] = dict()


@view_config(route_name="admin_add_application", renderer='json', request_method='POST')
def add_application(request):
    try:
        application_name = request.json_body['name']
        application_description = request.json_body['description']
        application = dict()
        application['name'] = application_name
        application['description'] = application_description
        application['date'] = datetime.now()
        _init_applications_levels(application)
        application['levels']['DEBUG']['delete'] = 5
        application['levels']['INFO']['delete'] = 30
        application['levels']['WARN']['delete'] = 60
        application['levels']['ERROR']['archive'] = 90
        application['levels']['FATAL']['archive'] = 180

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
        _init_applications_levels(app)
        try:
            logger.debug(str(request.POST))
            for post_param in request.POST.keys():
                if post_param.endswith('_delete_days') or post_param.endswith('_archive_days'):
                    part = post_param.split('_')
                    level = part[0]
                    param_type = part[1]
                    if level + '_to_archive' in request.POST:
                        if param_type == 'archive':
                            app['levels'][level][param_type] = int(request.POST[post_param])
                    else:
                        if param_type == 'delete':
                            app['levels'][level][param_type] = int(request.POST[post_param])

            request.mongodb.applications.save(app, w=1)
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
