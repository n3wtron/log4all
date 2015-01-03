from pyramid.view import view_config

from log4all.model.stack import Stack


__author__ = 'Igor Maculan <n3wtron@gmail.com>'


@view_config(route_name='api_stack_get', renderer='json', request_method='GET')
def api_application_get(request):
    stack = Stack.get(request.db, {'sha': request.params['sha']})
    return stack