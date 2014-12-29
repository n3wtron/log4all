import logging

from pyramid.view import view_config

from log4all import Application


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

_log = logging.getLogger(__name__)


@view_config(route_name="api_applications_add", renderer='json', request_method="PUT")
def api_application_add(request):
    app = Application(request.json['name'], request.json['description'])
    app.save(request.db)
    return {"success": True,'application':app}