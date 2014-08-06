import logging

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from log4all.background.cleaner import logs_eraser_job
from log4all.background.notifications import notify_job
from log4all.background.stats import update_log_counter_by_application_job


__author__ = 'Igor Maculan <n3wtron@gmail.com>'


logger = logging.getLogger('log4all.background')
scheduler = None


def init_scheduler(settings):
    jobstores = {
        'default': MongoDBJobStore()
    }
    global scheduler
    scheduler = BackgroundScheduler(jobstores=jobstores)
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
    scheduler.start()


def shutdown_scheduler():
    global scheduler
    if scheduler:
        logger.info("stopping scheduler..")
        scheduler.shutdown()
        logger.info("scheduler stopped")