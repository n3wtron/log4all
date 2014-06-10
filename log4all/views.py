import logging
from bson import ObjectId
from pyramid.view import view_config

logger = logging.getLogger('log4all')

@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def detail_view(request):
    try:
        if request.registry.settings['db.type'] == 'mongodb':
            logs = list(request.mongodb.logs.find({'_id': ObjectId(request.GET['id'])}))
            log=logs[0]
            logger.debug("Log:"+str(log))
            return {'log': log}
    except KeyError:
        return {'error': 'No id parameter found'}