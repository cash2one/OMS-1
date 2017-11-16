import time
import requests


def get(url, params=None, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.get(url=url, params=params, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def options(url, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.options(url=url, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def head(url, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.post(url=url, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def post(url, data=None, json=None, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.post(url=url, data=data, json=json, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def put(url, data=None, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.put(url=url, data=data, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def patch(url, data=None, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.patch(url=url, data=data, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res


def delete(url, **kwargs):
    try:
        current_date = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                time.time()))
        print("%s: %s" % (current_date, url))
        res = requests.delete(url=url, **kwargs)
    except BaseException as error:
        # raise error
        print(error)
        return ""
    return res
