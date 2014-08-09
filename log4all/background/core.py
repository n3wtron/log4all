import logging

from log4all.background.cleaner import logs_eraser_job
from log4all.background.majordomo import majordomo_job
from log4all.background.notifications import notify_job
from log4all.background.stats import update_log_counter_by_application_job
from log4all.background import scheduler

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

logger = logging.getLogger('log4all.background')


def init_scheduler(settings):
    scheduler.add_job(majordomo_job, 'cron',
                      args=[settings],
                      second='*/15',
                      max_instances=1,
                      id='majordomo',
                      replace_existing=True)

    scheduler.add_job(update_log_counter_by_application_job, 'cron',
                      args=[settings],
                      minute='*/1',
                      max_instances=1,
                      id='update_log_counter_by_application',
                      replace_existing=True)
    scheduler.add_job(logs_eraser_job, 'cron',
                      args=[settings],
                      minute='*/1',
                      max_instances=1,
                      id='logs_eraser',
                      replace_existing=True)
    scheduler.add_job(notify_job, 'cron',
                      args=[settings],
                      minute='*/1',
                      max_instances=1,
                      id='notify_job',
                      replace_existing=True)


def shutdown_scheduler():
    global scheduler
    if scheduler:
        logger.info("stopping scheduler..")
        scheduler.shutdown()
        logger.info("scheduler stopped")