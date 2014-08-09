import datetime
import time

from bson.objectid import ObjectId


__author__ = 'Igor Maculan <n3wtron@gmail.com>'

LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
LEVEL_COLORS = {'DEBUG': "#5abb71", 'INFO': '#00CCFF', 'WARN': '#FF9900', 'ERROR': '#FF0000', 'FATAL': '#000000'}

APPLICATION_STATUS_ACTIVE = 'active'
APPLICATION_STATUS_UNACTIVE = 'unative'
APPLICATION_STATUS_DELETING = 'deleting'

def adjust_record(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime.datetime):
        return time.mktime(data.timetuple())
    return data

def mongo_db_result_to_json(data):
    if isinstance(data, list):
        for d in data:
            d=mongo_db_result_to_json(d)
    else:
        if isinstance(data, dict):
            for k in data.keys():
                data[k]=mongo_db_result_to_json(data[k])
        else:
            data = adjust_record(data)
    return data