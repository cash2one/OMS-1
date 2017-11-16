# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from collaboration.services.order_service import OrderService
from oms_server.serializers.order_serializer import OrderSerializer
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.auth_utils import auth
from oms.extension.logger import time_logger


@api_view(['GET'])
@auth
@time_logger
def list(request):
    ''' 订单创建或获取列表 '''
    # user_id = request.user['id']
    data = request.GET
    page = int(data.get('page_index', 1))
    paginator = OrderService().\
        list(kwargs=data)
    paginator.current_page = page
    paginator.serializer = OrderSerializer
    return JsonResponse(paginator, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PATCH', 'PUT'])
@auth
def get_or_update(request, pk):
    ''' 订单获取详情或更新 '''
    # user_id = request.user['id']
    if request.method == 'GET':
        order = OrderService().get(order_id=pk)
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        result = OrderService().\
            update(order_id=pk, data=request.data)
        if result:
            serializer = OrderSerializer(result)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            data = None
            return JsonResponse(data, msg='failed', status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def lock_order(request, pk):
    ''' 订单锁定 '''
    # user_id = request.user['id']
    lock_reanson = request.data.get('lock_reanson')
    order = OrderService().\
        lock_order(order_id=pk, lock_reanson=lock_reanson)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def unlock_order(request, pk):
    ''' 订单解锁 '''
    # user_id = request.user['id']
    order = OrderService().unlock_order(order_id=pk)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def check_order(request, pk):
    ''' 订单审核 '''
    # user_id = request.user['id']
    # token = request.user['token']
    order = OrderService().order_check(order_id=pk)
    orders = OrderService().route_order(order_id=order.id)
    serializer = OrderSerializer(orders, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
