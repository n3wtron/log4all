import logging
import pymongo
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from log4all.models import initialize_sql


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    logging.getLogger('log4all').debug(str(settings))
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    #Mongo if present
    if settings['db.type'] == 'mongodb':
        config.registry.mongo_conn = pymongo.Connection(host=settings['mongodb.hostname'])

        def mongo_db(request):
            db = config.registry.mongo_conn['log4all']
            return db
        config.add_request_method(mongo_db, 'mongodb', reify=True)
    else:
        #SqlAlchemy
        config.scan('log4all.models')
        sql_engine = engine_from_config(settings,prefix='sqlalchemy.')
        initialize_sql(sql_engine)
        config.registry.sql_conn = sessionmaker(bind=sql_engine)

        def sql_db(request):
            maker = request.registry.sql_conn
            session = maker()

            def cleanup(finished_request):
                if finished_request.exception is not None:
                    session.rollback()
                else:
                    session.commit()
            request.add_finished_callback(cleanup)
            return session
        config.add_request_method(sql_db,'sqldb',reify=True)

    #Routing
    config.add_route('home', '/')
    config.add_route('api_logs_add', '/api/logs/add')
    config.add_route('api_logs_search', '/api/logs/search')
    config.scan()
    return config.make_wsgi_app()
