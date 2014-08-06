import logging

import pymongo

from log4all.notifications import notification_classes


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all.background')


def notify_job(settings):
    db_cl = pymongo.Connection(host=settings['mongodb.hostname'])
    try:
        db = db_cl[settings['mongodb.dbname']]
        notifications = db.notifications.find().sort([('date', pymongo.ASCENDING)])
        notif_to_delete = list()
        for notif in notifications:
            users = db.users.find({'groups': {'$in': notif['groups']}})
            notif_to_delete.append(notif['_id'])
            for user in users:
                for notif_type in user['notifications']:
                    if notif_type in notification_classes:
                        notificator = notification_classes[notif_type](settings)
                        notificator.notify(notif['log_id'], user=user)
                    else:
                        logger.error("Notification class not found for notification type:" + notif_type)

        # Removing notifications
        db.notifications.remove({'_id': {'$in': notif_to_delete}})

    finally:
        db_cl.close()