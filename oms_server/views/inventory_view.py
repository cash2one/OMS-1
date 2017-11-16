# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.services.inventory_service import InventoryService
from oms.extension.response_wrapper import JsonResponse
from oms_server.serializers.sku_serializer import SkuSerializer
from oms_server.extension.auth_utils import auth
from oms.extension.logger import time_logger


# 获取库存列表
@api_view(['GET'])
@auth
@time_logger
def list(request):
    user_id = request.user['id']
    if request.method == 'GET':
        param = request.query_params
        page = request.query_params.get('page_index', 1)
        paginator = InventoryService().\
            list(user_id=user_id, param=param)
        paginator.current_page = page
        paginator.serializer = SkuSerializer
        return JsonResponse(data=paginator, status=status.HTTP_200_OK)


# 测试库存创建
@api_view(['POST'])
@auth
@time_logger
def create(request):
    user_id = request.user['id']
    sku_id = request.data['sku_id']
    warehouse_id = request.data['warehouse_id']
    quantity = request.data['quantity']
    inventory = InventoryService().\
        create(user_id=user_id, sku_id=sku_id, warehouse_id=warehouse_id, quantity=quantity)
    serializer = InvetorySerializer(inventory)
    return JsonResponse(data=serializer.data)
