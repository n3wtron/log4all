import logging

from pyramid.view import view_config

from log4all.model.application import Application
from log4all.util.json_util import jsonizer


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='helper_applications_autocomplete', renderer='json', request_method="GET")
def api_applications_autocomplete(request):
    search_str = request.params.get('searchstr')
    single = request.params.get('single') == 'true'
    if not single:
        partial_src = search_str.split(',')[-1]
    else:
        partial_src = search_str
    applications = Application.search(request.db, {'name': {'$regex': partial_src.strip()}})
    results = list()
    for app in applications:
        result = {}
        if not single:
            result['field'] = ''.join(search_str.split(',')[:-1]) + ',' + app.name
            if result['field'][0] == ',':
                result['field'] = result['field'][1:]
        else:
            result['field'] = app.name
        results.append(jsonizer(result))
    return {'results': results}