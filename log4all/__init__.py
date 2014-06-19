import logging
from gunicornwebsocket.python_fixes import SocketIO
import pymongo
from pymongo.errors import CollectionInvalid
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from socketio.server import SocketIOServer

log4all_session_factory = UnencryptedCookieSessionFactoryConfig('log4allsession')


def init_db(db):
    db.tags.ensure_index('name', unique=True)
    db.logs.ensure_index('date')
    db.stacks.ensure_index('hash_stacktrace', unique=True)
    try:
        db.create_collection('tail_logs', capped=True, size=268435456)
    except CollectionInvalid:
        pass
    db.tail_logs.ensure_index('date')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, session_factory=log4all_session_factory)
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.registry.mongo_conn = pymongo.Connection(host=settings['mongodb.hostname'])
    init_db(config.registry.mongo_conn['log4all'])

    def mongo_db(request):
        db = config.registry.mongo_conn['log4all']
        return db

    config.add_request_method(mongo_db, 'mongodb', reify=True)

    # Routing
    config.add_route('home', '/')
    config.add_route('result_table', '/result')
    config.add_route('tail_table', '/tail')
    config.add_route('detail', '/detail')
    config.add_route('detail_send_notification', '/detail_send_notification')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.add_route('api_logs_tail', '/api/logs/tail')
    config.add_route('helper_tags_search', '/helper/tags/search')

    config.scan()
    app = config.make_wsgi_app()
    return app
