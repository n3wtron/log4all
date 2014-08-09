from datetime import datetime
import logging

from bson import ObjectId
import pymongo
from pymongo.errors import DuplicateKeyError
from pyramid.view import view_config

from log4all.background import majordomo

from log4all.util import mongo_db_result_to_json, LEVEL_COLORS, LEVELS, APPLICATION_STATUS_ACTIVE, \
    APPLICATION_STATUS_DELETING


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all')


@view_config(route_name='admin_home', renderer='templates/home.jinja2')
def admin_home(request):
    return {}


@view_config(route_name='admin_applications', renderer='templates/applications.jinja2')
def admin_applications(request):
    error_messages = list()
    if request.method == 'POST':
        if request.POST['operation'] == 'addApplication':
            application = dict()
            application['name'] = request.POST['name']
            application['description'] = request.POST['description']
            application['date'] = datetime.now()
            application['status'] = APPLICATION_STATUS_ACTIVE
            application['stat'] = dict()
            _init_applications_levels(application)
            application['levels']['DEBUG']['delete'] = 5
            application['levels']['INFO']['delete'] = 30
            application['levels']['WARN']['delete'] = 60
            application['levels']['ERROR']['archive'] = 90
            application['levels']['FATAL']['archive'] = 180
            try:
                request.mongodb.applications.insert(application, w=1, continue_on_error=False)
            except DuplicateKeyError as e:
                logger.exception(e)
                error_messages.append(e.message)
        if request.POST['operation'] == 'delApplication':
            try:
                request.mongodb.applications.update({'name': request.POST['name']},
                                                    {'$set': {'status': APPLICATION_STATUS_DELETING}})
                majordomo.insert_opertation(request.mongodb, majordomo.OP_DELETE_APPLICATION,
                                            {'application_name': request.POST['name']})
            except DuplicateKeyError as e:
                logger.exception(e)
                error_messages.append(e.message)

    apps = mongo_db_result_to_json(
        list(request.mongodb.applications.find({'status': APPLICATION_STATUS_ACTIVE}).sort('name')))
    error_message = ""
    for err in error_messages:
        error_message += err + "</br>"
    return {
        'csrf': request.session.get_csrf_token(),
        'applications': apps,
        'error_message': error_message
    }


def _init_applications_levels(app):
    application_levels = dict()
    app['levels'] = application_levels
    application_levels['DEBUG'] = dict()
    application_levels['INFO'] = dict()
    application_levels['WARN'] = dict()
    application_levels['ERROR'] = dict()
    application_levels['FATAL'] = dict()


@view_config(route_name="admin_edit_application", renderer='templates/application.jinja2')
def edit_application(request):
    result = dict()
    if request.method == 'POST' and 'csrf' in request.POST and request.POST['csrf'] == request.session.get_csrf_token():
        # Modification from Form
        app = request.mongodb.applications.find_one({'_id': ObjectId(request.params['idApp'])})
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
    result['levels'] = LEVELS
    result['level_colors'] = LEVEL_COLORS
    return result


@view_config(route_name="admin_stats", renderer='templates/stats.jinja2')
def stats(request):
    apps = request.mongodb.applications.find().sort([('n_logs', pymongo.DESCENDING)])
    app_stats = dict()
    if not 'type' in request.GET:
        stat_type = 'simple'
    else:
        stat_type = request.GET['type']
    for app in apps:
        try:
            app_stats[app['name']] = app['stat']
        except KeyError:
            app_stats[app['name']] = dict(n_logs=0, levels=dict())
    return {'type': stat_type, 'stats': app_stats, 'levels': LEVELS, 'level_colors': LEVEL_COLORS}