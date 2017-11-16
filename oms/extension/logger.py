# -*- coding:utf-8 -*-
import time
import logging

__time_logger = logging.getLogger('time_logger')


def time_logger(func):
    def inner(*args, **kwargs):
        t1 = time.time()
        span = -1
        try:
            result = func(*args, **kwargs)
            t2 = time.time()
            span = t2 - t1
            return result
        except Exception as e:
            t2 = time.time()
            span = t2 - t1
            raise e
        finally:
            __time_logger.info("function [" + func.__name__ +
                               "] cost time:" + str(round(span, 3)))
    return inner


logger = logging.getLogger('custom')
