import logging
import pymongo
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
log4all_session_factory = UnencryptedCookieSessionFactoryConfig('log4allsession')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings,session_factory=log4all_session_factory)
    logging.getLogger('log4all').debug(str(settings))
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.registry.mongo_conn = pymongo.Connection(host=settings['mongodb.hostname'])

    def mongo_db(request):
        db = config.registry.mongo_conn['log4all']
        return db
    config.add_request_method(mongo_db, 'mongodb', reify=True)

    #Routing
    config.add_route('home', '/')
    config.add_route('result_table', '/result')
    config.add_route('detail', '/detail')
    config.add_route('detail_send_notification', '/detail_send_notification')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.add_route('helper_tags_search', '/helper/tags/search')
    config.scan()
    return config.make_wsgi_app()
