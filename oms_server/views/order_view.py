# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.services.order_service import OrderService
from oms_server.serializers.order_serializer import OrderDetailSerializer
from oms_server.serializers.order_serializer import OrderSerializer
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.auth_utils import auth
from oms.extension.logger import time_logger


# 测试接口
@api_view(['GET', 'POST'])
def test(request):
    # from oms_server.http_service.user_service import get_user_info
    # result = get_user_info(10000005)
    from oms_server.tasks import cop_retry, error_handler
    cop_retry.apply_async(
                        ('1', '2', '3', '3'),
                        retry=True, max_retries=3, link_error=error_handler.s())
    return JsonResponse(data="result")


# 创建订单 和　获取订单列表
@api_view(['POST', 'GET'])
@auth
@time_logger
def create_or_list(request):
    ''' 订单创建或获取列表 '''
    user_id = request.user['id']
    user_name = request.user['nickname']
    if request.method == 'POST':
        order = OrderService().\
            create(user_id=user_id, data=request.data, user_name=user_name)
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'GET':
        data = request.GET
        page = int(data.get('page_index', 1))
        paginator = OrderService().\
            list(user_id=user_id, kwargs=data)
        paginator.current_page = page
        paginator.serializer = OrderSerializer
        return JsonResponse(paginator, status=status.HTTP_200_OK)


# 获取订单详情或者编辑订单
@api_view(['GET', 'POST', 'PATCH', 'PUT'])
@auth
def get_or_update(request, pk):
    ''' 订单获取详情或更新 '''
    user_id = request.user['id']
    if request.method == 'GET':
        order = OrderService().get(user_id=user_id, order_id=pk)
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        result = OrderService().\
            update(user_id=user_id, order_id=pk, data=request.data)
        if result:
            serializer = OrderSerializer(result)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            data = None
            return JsonResponse(data, msg='failed', status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        print("patch")
        order = OrderService().patch_update(order_id=pk, data=request.data)
        serializer = OrderSerializer(order)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def lock_order(request, pk):
    ''' 订单锁定 '''
    user_id = request.user['id']
    lock_reanson = request.data.get('lock_reanson')
    order = OrderService().\
        lock_order(user_id=user_id, order_id=pk, lock_reanson=lock_reanson)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def unlock_order(request, pk):
    ''' 订单解锁 '''
    user_id = request.user['id']
    order = OrderService().unlock_order(user_id=user_id, order_id=pk)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def withdraw_order(request, pk):
    ''' 订单撤回 '''
    user_id = request.user['id']
    order = OrderService().withdraw_order(user_id=user_id, order_id=pk)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def delete_order(request, pk):
    ''' 删除订单 '''
    user_id = request.user['id']
    order = OrderService().delete_order(user_id=user_id, order_id=pk)
    serializer = OrderSerializer(order)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@auth
def get_order_details(request):
    ''' 获取订单详情(废弃) '''
    order_id = 1
    order_details = OrderService().get_sku_infoes(order_id=order_id)
    serializer = OrderDetailSerializer(order_details, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def check_order(request, pk):
    ''' 订单审核 '''
    user_id = request.user['id']
    token = request.user['token']
    order = OrderService().order_check(user_id=user_id, order_id=pk)
    orders = OrderService().route_order(user_id=user_id, order_id=order.id, token=token)
    serializer = OrderSerializer(orders, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
