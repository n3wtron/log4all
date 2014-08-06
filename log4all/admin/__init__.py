__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def add_route(config):
    config.add_route('admin_home', '/admin/')
    config.add_route('admin_edit_application', '/admin/application')
    config.add_route('admin_stats', '/admin/stats')
    config.add_route('admin_applications', '/admin/applications')

    config.add_route('admin_groups', '/admin/groups')
    config.add_route('admin_users', '/admin/users')
    config.add_route('admin_edit_user', '/admin/user')
    config.add_route('admin_edit_group', '/admin/group')