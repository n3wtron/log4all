from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

jobstores = {
    'default': MongoDBJobStore(),
    'RAMJobStore': MemoryJobStore()
}

scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()