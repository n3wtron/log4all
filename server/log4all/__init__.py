import pymongo
from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.registry.conn = pymongo.Connection(host='localhost')

    def open_db(request):
        db = config.registry.conn['log4all']
        return db

    config.add_request_method(open_db, 'db', reify=True)

    config.add_route('home', '/')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.scan()
    return config.make_wsgi_app()
