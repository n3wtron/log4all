from pyramid.view import view_config
from log4all.model.log import Log


@view_config(route_name='home', renderer='templates/index.jinja2')
def home_view(request):
    return {}



@view_config(route_name='admin_js', renderer='admin_templates/js/admin_log4all.jsinja2')
def admin_js(request):
    return {}

@view_config(route_name='admin', renderer='admin_templates/index.jinja2')
def admin_view(request):
    return {}

@view_config(route_name='admin_applications', renderer='admin_templates/applications.jinja2')
def admin_applications_view(request):
    return {}

@view_config(route_name='admin_application_edit', renderer='admin_templates/application.jinja2')
def admin_application_view(request):
    return {}