import json
from datetime import datetime
# import pika
from django.utils import six
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from oms.extension.exception import CustomException
from oms.extension.exception import NotExistException
from oms.extension.exception import PingppException
from oms.extension.logger import logger


class JsonResponse(Response):

    def __init__(self, data=None, code=0, msg='success',
                 status=None, success=True,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'Use serialized `.data` or `.error`. representation.'
            )
            raise AssertionError(msg)
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
                print(name, value)
                print("-----------------------")
                self[name] = value


def send_bug_to_wechat(bug):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')  # 默认端口5672，可不写
        )
    # 声明一个管道，在管道里发消息
    channel = connection.channel()
    # 在管道里声明queue
    channel.queue_declare(queue='bug_message')
    # RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange='',
                          routing_key='bug_message',  # queue名字
                          body=json.dumps(bug))  # 消息内容
    connection.close()  # 队列关闭


# 异常处理
def custom_exception_handler(exc, context):

    import traceback

    print('*****************************')
    traceback.print_exc()
    error_code = -1
    error_message = 'There were some strange mistakes!'
    _status = status.HTTP_500_INTERNAL_SERVER_ERROR
    _result = {}
    if isinstance(exc, CustomException):
        error_code = exc.error_code
        error_message = exc.error_message
        _status = status.HTTP_200_OK
    elif isinstance(exc, ObjectDoesNotExist):
        exc = NotExistException(exc)
        error_code = exc.error_code
        error_message = exc.error_message
        _status = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PingppException):
        error_code = 60007
        error_message = str(exc)
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        error_code = -1
        error_message = str(exc)
    data = {
            'error_message': error_message,
            'error_code': error_code,
            'result': _result,
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'success': False
        }
    response = Response(data=data, status=_status)
    try:
        pass
        # response.data['url'] = context['request']._request.get_full_path()
        # send_bug_to_wechat(response.data)
    except Exception as e:
        print(e)
        print('Reduce a bug, but not important, Please ignore it!')
    return response
