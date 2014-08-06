from datetime import datetime, timedelta
import logging
import os
from bson import json_util
import pymongo


logger = logging.getLogger('log4all.background')

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def delete_old_logs(db, application, level, before):
    del_qry = {'application': application, 'level': level, 'date': {'$lte': before}}
    logger.debug("Removing " + str(del_qry))
    db.logs.remove(del_qry)


def archive_old_logs(db, arch_path, application, level, before):
    if arch_path is None:
        logger.error("Cannot archive archive.dir doesn't set")
        return
    app_arch_path = arch_path + os.sep + application
    if not os.path.exists(app_arch_path):
        os.makedirs(app_arch_path)
    with open(app_arch_path + os.sep + level + "_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.dump', 'w') \
            as app_dump_file:
        arch_qry = {'application': application, 'level': level, 'date': {'$lte': before}}
        logger.debug("Archiving " + str(arch_qry))
        arch_logs = db.logs.find(arch_qry)
        app_dump_file.write(json_util.dumps(arch_logs))


def logs_eraser_job(settings):
    db_cl = pymongo.Connection(host=settings['mongodb.hostname'])
    try:
        db = db_cl[settings['mongodb.dbname']]
        # retrieve application information
        apps = db.applications.find()
        for app in apps:
            for level in app['levels'].keys():
                if 'delete' in app['levels'][level]:
                    # DELETE
                    del_date = datetime.now() - timedelta(days=app['levels'][level]['delete'])
                    delete_old_logs(db, app['name'], level, del_date)
                if 'archive' in app['levels'][level]:
                    # ARCHIVE
                    arch_date = datetime.now() - timedelta(days=app['levels'][level]['archive'])
                    archive_old_logs(db, settings['archive.path'], app['name'], level, arch_date)
                    delete_old_logs(db, app['name'], level, arch_date)
    finally:
        db_cl.close()