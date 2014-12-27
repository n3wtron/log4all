import logging
from pyramid.view import view_config
from log4all.util.json_util import jsonizer
from log4all.model.application import Application
__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='helper_applications_autocomplete', renderer='json', request_method="GET")
def api_applications_autocomplete(request):
    search_str = request.params.get('searchstr')
    return {'results':[jsonizer(app) for app in Application.search(request.db,{'name':{'$regex':search_str}})]}