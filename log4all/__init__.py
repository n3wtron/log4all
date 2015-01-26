from datetime import datetime, timedelta
from urllib.parse import urlparse

from gridfs import GridFS
import pymongo
from pyramid.config import Configurator

from log4all.model.application import Application
from log4all.model.log import Log
from log4all.model.stack import Stack
from log4all.model.tag import Tag


applications = None
dt_applications_updated = None


def init_db(db):
    """
    Database Initialization
    :param db:mongodb connection
    """
    Log.init(db)
    Stack.init(db)
    Tag.init(db)
    Application.init(db)


def init_routing(config):
    """
    Routing initialization
    :param config: pyramid configuration
    """

    config.add_route('home', '/')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.add_route('api_logs_tail', '/api/logs/tail')
    config.add_route('helper_applications_autocomplete', 'api/applications/autocompleteSearch')
    config.add_route('api_applications_add', '/api/applications/add')
    config.add_route('api_applications_all', '/api/applications')

    config.add_route('api_application_get', '/api/application/get')
    config.add_route('api_application_delete', '/api/application/delete')
    config.add_route('api_application_update', '/api/application/update')
    config.add_route('api_tags_get', '/api/tags')
    config.add_route('api_stack_get', '/api/stack')

    config.add_route('admin', '/admin')
    config.add_route('admin_js', '/admin/js/admin_log4all.js')
    config.add_route('admin_applications', '/admin/applications')
    config.add_route('admin_application_edit', '/admin/application/edit')


def init_log4all(config):
    """
    Log4all initialization, request_method and db initialization
    :param config: pyramid configuration
    """
    db_url = urlparse(config.get_settings()['mongo_uri'])
    config.registry.db = pymongo.Connection(host=db_url.hostname, port=db_url.port)

    def get_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    def get_gridfs(request):
        return GridFS(request.db)

    def get_application(request, application_name=None):
        global applications
        global dt_applications_updated
        now = datetime.now()
        if applications is None or dt_applications_updated is None or application_name not in applications or \
                        dt_applications_updated < now - timedelta(seconds=30):
            # retrieve applications from db
            dt_applications_updated = now
            applications = dict()
            for app in Application.search(request.db):
                applications[app.name] = app
        return applications.get(application_name)

    init_db(get_db(None))

    config.add_request_method(get_db, 'db', reify=True)
    config.add_request_method(get_gridfs, 'gridfs', reify=True)
    config.add_request_method(get_application, 'applications')


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_renderer('.jsinja2', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('admin_static', 'admin_static', cache_max_age=3600)
    config.add_static_view('bower_components', 'bower_components', cache_max_age=3600)

    init_log4all(config)

    init_routing(config)

    config.scan()
    return config.make_wsgi_app()
