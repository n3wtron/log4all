from datetime import datetime
import logging

import pymongo

from log4all.background import scheduler


__author__ = 'Igor Maculan <n3wtron@gmail.com>'
logger = logging.getLogger('log4all.background')

STATUS_NEW = 'new'
STATUS_EXECUTING = 'executing'
OP_DELETE_APPLICATION = 'delete_application'
OP_DELETE_GROUP = 'delete_group'


def insert_opertation(db, operation, params):
    majordomo_op = dict(operation=operation,
                        params=params,
                        status=STATUS_NEW,
                        dt_insert=datetime.now())
    db.majordomo.insert(majordomo_op)


def _remove_operation(db, op):
    db.majordomo.remove({'_id': op['_id']})


def _set_operation_in_error(db, op, error):
    db.majordomo.update({'_id': op['_id']}, {'$set': {'status': error}})


def majordomo_job(settings):
    with pymongo.Connection(host=settings['mongodb.hostname']) as db_cl:
        db = db_cl[settings['mongodb.dbname']]
        operations = list(
            db.majordomo.find(
                {'status': STATUS_NEW},
                sort=[('dt_insert', pymongo.ASCENDING)],
                limit=10)
        )

        for op in operations:
            logger.debug('Majordomo: elaborating operation:' + str(op))
            if op['operation'] in operation_map:
                scheduler.add_job(operation_map[op['operation']],
                                  trigger=None,
                                  args=[settings, op],
                                  jobstore='RAMJobStore')
                db.majordomo.update({'_id': op['_id']},
                                    {
                                        '$set': {
                                            'status': STATUS_EXECUTING,
                                            'dt_execution': datetime.now()
                                        }
                                    },
                                    w=1)


# MAJORDOMO JOBS


def remove_application_job(settings, op):
    with pymongo.Connection(host=settings['mongodb.hostname']) as db_cl:
        try:
            logging.info("removing application logs for:" + str(op['params']['application_name']))
            db = db_cl[settings['mongodb.dbname']]
            db.logs.remove({'application': op['params']['application_name']})
            db.applications.remove({'name': op['params']['application_name']})
            _remove_operation(db, op)
        except Exception as e:
            _set_operation_in_error(db, op, e.message)


def remove_group_job(settings, op):
     with pymongo.Connection(host=settings['mongodb.hostname']) as db_cl:
        try:
            group_name=op['params']['group_name']
            logging.info("removing group :" + str(group_name))
            db = db_cl[settings['mongodb.dbname']]
            db.notifications.remove({'groups': group_name}, {'$pull': {'groups': group_name}}, multi=True)
            _remove_operation(db, op)
        except Exception as e:
            _set_operation_in_error(db, op, e.message)


operation_map = {
    OP_DELETE_APPLICATION: remove_application_job,
    OP_DELETE_GROUP : remove_group_job
}