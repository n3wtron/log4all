import datetime
import time

from bson.objectid import ObjectId


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
LEVEL_COLORS = {'DEBUG': "#99CCCC", 'INFO': '#00CCFF', 'WARN': '#FF9900', 'ERROR': '#FF0000', 'FATAL': '#000000'}


def adjust_record(data):
    for k in data.keys():
        if isinstance(data[k], ObjectId):
            data[k] = str(data[k])
        if isinstance(data[k], datetime.datetime):
            data[k] = time.mktime(data[k].timetuple())


def mongo_db_result_to_json(data):
    if isinstance(data, list):
        for d in data:
            adjust_record(d)
    else:
        adjust_record(data)
    return data