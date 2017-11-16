# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse
from oms_server.services.stock_in_service import StockInService
from oms_server.serializers.stock_in_serializer import StockInSerializer
from oms_server.extension.auth_utils import auth
from oms.extension.logger import time_logger


# 获取入库单列表
@api_view(['GET', 'POST'])
@auth
@time_logger
def create_or_list(request):
    user_id = request.user['id']
    user_name = request.user['nickname']
    token = request.user['token']
    if request.method == 'POST':
        stock_in = StockInService().\
            create(user_id=user_id, token=token,
                   data=request.data, user_name=user_name)
        serializer = StockInSerializer(stock_in)
        return JsonResponse(data=serializer.data,
                            status=status.HTTP_201_CREATED)
    elif request.method == 'GET':
        page = request.GET.get('page_index', 1)
        paginator = StockInService().\
            list(user_id=user_id, param=request.GET)
        paginator.current_page = page
        paginator.serializer = StockInSerializer
        return JsonResponse(data=paginator, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@auth
@time_logger
def get_or_update(request, pk):
    user_id = request.user['id']
    if request.method == 'POST':
        stock_in = StockInService().\
            update(user_id=user_id, stock_in_id=pk, data=request.data)
        serializer = StockInSerializer(stock_in)
        return JsonResponse(data=serializer.data,
                            status=status.HTTP_200_OK)
    elif request.method == 'GET':
        stock_in = StockInService().\
            get(user_id=user_id, stock_in_id=pk)
        serializer = StockInSerializer(stock_in)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
@auth
@time_logger
def delete(request,pk):
    user_id = request.user['id']
    stock_in = StockInService().delete(user_id=user_id, stock_in_id=pk)
    serializer = StockInSerializer(stock_in)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@auth
@time_logger
def cancle(request,pk):
    user_id = request.user['id']
    stock_in = StockInService().\
        cancle(user_id=user_id,stock_in_id=pk)
    serializer = StockInSerializer(stock_in)
    return JsonResponse(serializer.data,status=status.HTTP_200_OK)













