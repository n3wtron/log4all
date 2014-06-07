from pyramid.paster import get_app, setup_logging
ini_path = '/home/igor/projects/python/projects/log4all/server/production.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
