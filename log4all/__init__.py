from gridfs import GridFS
import pymongo
from pyramid.config import Configurator

from log4all.model.application import Application
from log4all.model.log import Log
from log4all.model.stack import Stack
from log4all.model.tag import Tag


try:
    # for python 2
    from urlparse import urlparse
except ImportError:
    # for python 3
    from urllib.parse import urlparse


def initdb(db):
    """
    Database Initialization
    :param db:
    """
    Log.init(db)
    Stack.init(db)
    Tag.init(db)
    Application.init(db)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_renderer('.jsinja2', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('admin_static', 'admin_static', cache_max_age=3600)
    config.add_static_view('bower_components', 'bower_components', cache_max_age=3600)

    # MongoDB
    db_url = urlparse(settings['mongo_uri'])
    config.registry.db = pymongo.Connection(host=db_url.hostname, port=db_url.port)

    def get_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    def get_gridfs(request):
        return GridFS(request.db)

    initdb(get_db(None))

    config.add_request_method(get_db, 'db', reify=True)
    config.add_request_method(get_gridfs, 'gridfs', reify=True)

    # Routing
    config.add_route('home', '/')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.add_route('helper_applications_autocomplete', 'api/applications/autocompleteSearch')
    config.add_route('api_applications_add', '/api/applications/add')
    config.add_route('api_applications_all', '/api/applications')

    config.add_route('admin', '/admin')
    config.add_route('admin_js', '/admin/js/admin_log4all.js')
    config.add_route('admin_applications', '/admin/applications')
    config.add_route('admin_application_edit', '/admin/application/edit')
    config.add_route('api_application_get', '/admin/application/get')



    config.scan()
    return config.make_wsgi_app()
