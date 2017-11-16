# -*- coding: utf-8 -*-
import time
import datetime
import logging

logger = logging.getLogger('custom.formatter')


def get_today():
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    return today


def get_yesterday():
    today = get_today()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday


def get_tomorrow():
    today = get_today()
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow


def uuid_to_str(uid):
    ''' uuid转字符串，去掉横杠 '''
    return str(uid).replace('-', '')


def str_to_bool(s):
    ''' 字符串转布尔值 '''
    if isinstance(s, str):
        if s == 'True' or s == 'true' or s == '1':
            return True
        elif s == 'False' or s == 'false' or s == '0':
            return False
        else:
            return None
    else:
        return None


def datetime_to_str(dt):
    ''' 日期转字符串YYYY-MM-DD HH:MM:SS '''
    if dt is None:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def timestamp_to_datetime(ts):
    ''' 时间戳转日期格式 '''
    if not ts:
        return None
    try:
        struct_time = time.localtime(int(ts))
        dt = datetime.datetime(*struct_time[:6])
    except Exception as e:
        print("wrong")
        logger.warning('时间戳转日期错误:' % str(e))
    return dt
