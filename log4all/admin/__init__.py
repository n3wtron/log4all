__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def add_route(config):
    config.add_route('admin_home', '/admin/')
    config.add_route('admin_edit_application', '/admin/application')
    config.add_route('admin_applications', '/admin/applications')
    config.add_route('admin_add_application', '/admin/api/applications/add')
    config.add_route('admin_get_applications', '/admin/api/applications/get')