# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse
from oms_server.serializers.stock_in_serializer import StockInSerializer
from oms_server.extension.auth_utils import auth
from oms.extension.logger import time_logger
from collaboration.services.stock_in_service import StockInService


# 获取入库单列表
@api_view(['GET', 'POST'])
@auth
@time_logger
def list(request):
    # user_id = request.user['id']
    # token = request.user['token']
    page = request.GET.get('page_index', 1)
    paginator = StockInService().\
        list(param=request.GET)
    paginator.current_page = page
    paginator.serializer = StockInSerializer
    return JsonResponse(data=paginator, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@auth
@time_logger
def get_or_update(request, pk):
    # user_id = request.user['id']
    if request.method == 'POST':
        stock_in = StockInService().\
            update(stock_in_id=pk, data=request.data)
        serializer = StockInSerializer(stock_in)
        return JsonResponse(data=serializer.data,
                            status=status.HTTP_200_OK)
    elif request.method == 'GET':
        stock_in = StockInService().\
            get(stock_in_id=pk)
        serializer = StockInSerializer(stock_in)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
@auth
@time_logger
def delete(request, pk):
    # user_id = request.user['id']
    stock_in = StockInService().delete(stock_in_id=pk)
    serializer = StockInSerializer(stock_in)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
