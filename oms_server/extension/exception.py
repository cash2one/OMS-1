# -*- coding: UTF-8 -*-
from rest_framework.exceptions import APIException
from oms.extension.error_code import ERROR_MSG


class ServiceUnavailable(APIException):

    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class CustomException(Exception):

    def __init__(self, error_code, error_message=None):
        self.error_code = error_code
        if error_message is None:
            self.error_message = ERROR_MSG.get(
                int(error_code), 'opps: somethine wrong!')
        else:
            self.error_message = error_message


class ErrorResult:

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message if error_message\
            else ERROR_MSG.get(error_code)
