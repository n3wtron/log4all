__author__ = 'Igor Maculan <n3wtron@gmail.com>'
import logging

from bson import ObjectId
from pyramid.view import view_config

from log4all import Application


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name='api_application_update', renderer='json', request_method='POST')
def api_application_update(request):
    # check if app exist
    app = Application.search({"_id": ObjectId(request.json['_id'])})
    if app is None:
        return {'success': False, 'message': 'No application found with id:' + request.json['_id']}
    app = Application.from_bson(request.json)
    try:
        app.save(request.db)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}