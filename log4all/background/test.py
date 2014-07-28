import time
from datetime import datetime

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def hello():
    print str(datetime.now())+" hello"
    time.sleep(60)


