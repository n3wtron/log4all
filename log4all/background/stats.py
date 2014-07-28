from datetime import datetime
import logging

import pymongo


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
logger = logging.getLogger('log4all.background')


def update_log_counter_by_application(settings):
    db_cl = pymongo.Connection(host=settings['mongodb.hostname'])
    try:
        db = db_cl[settings['mongodb.dbname']]
        app_num_logs = db.logs.aggregate({
            '$group': {
                '_id': {
                    'application': '$application',
                    'level': '$level'
                },
                'count': {
                    '$sum': 1
                }
            }
        })
        stats = dict()
        for app_n_log in app_num_logs['result']:
            logger.debug('Update Application ' + str(app_n_log['_id']) + 'n_log:' + str(app_n_log['count']))
            app = app_n_log['_id']['application']
            if app not in stats:
                stats[app] = dict(n_logs=0, levels=dict(), updated=datetime.now())

            stats[app]['levels'][app_n_log['_id']['level']] = app_n_log['count']
            stats[app]['n_logs'] += app_n_log['count']

        all_apps = [a['name'] for a in db.applications.find({}, ['name'])]
        for app in all_apps:
            if app in stats:
                db.applications.update({'name': app}, {'$set': {'stat': stats[app]}})
            else:
                db.applications.update({'name': app},
                                       {'$set': {'stat': dict(updated=datetime.now(), levels=dict(), n_logs=0)}})
    finally:
        db_cl.close()