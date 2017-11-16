# -*- coding: UTF-8 -*-
import time
from datetime import datetime
from django.utils import six
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import exception_handler
from rest_framework.serializers import Field, CharField
from rest_framework import status
from oms_server.extension.exception import CustomException
from oms_server.extension.exception import ErrorResult


class TimestampField(Field):

    def to_internal_value(self, data):
        result = datetime.fromtimestamp(data)
        return result

    def to_representation(self, value):
        if isinstance(value, str):
            value = time.strptime(value, "%Y-%m-%d %H:%M:%S")
            return int(time.mktime(value))

        return int(time.mktime(value.timetuple()))


class StatusField(Field):

    def to_internal_value(self, data):
        return int(data)

    def to_representation(self, value):
        if isinstance(value, int):
            return str(value)
        return value


class UUIDField(CharField):

    def to_representation(self, value):
        return str(value).replace('-', '')


class UserCodeField(CharField):

    def to_representation(self, value):
        if value is None:
            return ''
        if value == '':
            return ''
        else:
            return value


class XMLResponse(Response):

    def __init__(self, data=None, code=0, msg='success',
                 status=None, success=True,
                 template_name=None, headers=None,
                 exception=False, content_type='application/xml'):
        super(Response, self).__init__(None, status=status)


# 响应包装
class JsonResponse(Response):

    def __init__(self, data=None, code=0, msg='success',
                 status=None, success=True,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            data = data.data
        if isinstance(data, Paginator):
            try:
                result_list = data.page(data.current_page)
            except PageNotAnInteger:
                result_list = data.page(1)
            except EmptyPage:
                result_list = data.page(data.num_pages)
            result = data.serializer(result_list, many=True).data
            data = {
                "total": data.count,
                "rows": result
            }
        if isinstance(data, ErrorResult):
            code = data.error_code
            msg = data.error_message
            success = False
            data = {}
        self.data = {
            "success": success,
            "error_code": code,
            "error_message": msg,
            "result": data,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value


# 异常处理
def custom_exception_handler(exc, context):

    print("Wrong.................")
    print(exc)

    response = exception_handler(exc, context)

    if response is not None:
        if response.data.get('detail'):
            response.data['error_msg'] = response.data['detail']
            del response.data['detail']  # 删除detail字段
        else:
            if isinstance(response.data, dict):
                data = {key: value for key, value in response.data.items()}
                response.data = {}
                response.data['err_msg'] = data
        response.data['code'] = response.status_code
        return response
    else:
        if isinstance(exc, CustomException):
            data = {
                'error_message': exc.error_message,
                'error_code': exc.error_code,
                'result': {},
                'current_time': datetime.now(),
                'success': False
            }
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {
                "error_message": str(exc),
                "error_code": -1,
                "result": {},
                "current_time": datetime.now(),
                "success": False
            }
            return Response(data=data,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)