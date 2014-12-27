from bson import ObjectId

__author__ = 'Igor Maculan <n3wtron@gmail.com>'

import datetime

import simplejson


def conv_datetime(v):
    return v.isoformat()


def conv_date(v):
    return v.strftime('%Y-%m-%d')


def identity(v):
    return v


def conv_bool(v):
    return v


def conv_dict_values(dic):
    result = {}
    for k in dic.keys():
        v = dic[k]
        result[k] = conv_autodetect(v)
    return result


def conv_list_values(v):
    result = []
    for e in v:
        result.append(conv_autodetect(e))
    return result

def conv_autodetect(v):
    return conv_bool(v) if type(v) == bool else \
        conv_datetime(v) if type(v) == datetime.datetime else \
        conv_dict_values(v) if type(v) == dict else \
        conv_list_values(v) if type(v) == list else \
        str(v) if type(v) == ObjectId else v


def jsonizer(obj, **kwargs):
    return conv_autodetect(obj)