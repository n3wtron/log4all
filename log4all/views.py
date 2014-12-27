from pyramid.view import view_config
from log4all.model.log import Log


@view_config(route_name='home', renderer='templates/index.jinja2')
def my_view(request):
    return {'project': 'log4all'}
