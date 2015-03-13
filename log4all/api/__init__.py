__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def init_api_url(config):
    config.add_route('api_logs_add_options', '/api/logs/add', request_method='OPTIONS')
    config.add_route('api_logs_add', '/api/logs/add', request_method='POST')

    config.add_route('api_logs_search_options', '/api/logs/search', request_method='OPTIONS')
    config.add_route('api_logs_search', '/api/logs/search', request_method='POST')

    config.add_route('api_logs_tail_options', '/api/logs/tail', request_method='OPTIONS')
    config.add_route('api_logs_tail', '/api/logs/tail', request_method='POST')

    config.add_route('helper_applications_autocomplete', 'api/applications/autocompleteSearch')

    #  ADMIN  #
    config.add_route('api_applications_all', '/api/applications', request_method='GET')
    config.add_route('api_applications_add', '/api/application', request_method='PUT')
    config.add_route('api_application_get', '/api/application/{applicationId}', request_method='GET')
    config.add_route('api_application_delete', '/api/application/{applicationId}', request_method='DELETE')
    config.add_route('api_application_update', '/api/application/{applicationId}', request_method='POST')

    config.add_route('api_groups_all', '/api/groups', request_method='GET')
    config.add_route('api_group_add', '/api/group', request_method='PUT')
    config.add_route('api_group_get', '/api/group/{groupId}', request_method='GET')
    config.add_route('api_group_delete', '/api/group/{groupId}', request_method='DELETE')
    config.add_route('api_group_update', '/api/group/{groupId}', request_method='POST')

    config.add_route('api_users_all', '/api/users', request_method='GET')
    config.add_route('api_users_add', '/api/user', request_method='PUT')
    config.add_route('api_user_get', '/api/user/{userId}', request_method='GET')
    config.add_route('api_user_delete', '/api/user/{userId}', request_method='DELETE')
    config.add_route('api_user_update', '/api/user/{userId}', request_method='POST')

    config.add_route('api_tags_get', '/api/tags')
    config.add_route('api_stack_get', '/api/stack')

    config.add_route('api_auth_login', '/api/auth/login')
    config.add_route('api_auth_permissions_list', '/api/auth/permissions')