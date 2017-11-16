# -*- coding: utf-8 -*-
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.serializers.sku_serializer import SkuSerializer
from oms_server.services.sku_service import SkuService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse

logger = logging.getLogger(__name__)


# 创建商品 和　获取商品列表
@api_view(['POST', 'GET'])
@auth
def create_or_list(request):
    user_id = request.user['id']
    if request.method == 'POST':
        sku = SkuService().\
            create(user_id=user_id,
                   param=request.data)
        serializer = SkuSerializer(sku)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'GET':
        page = request.GET.get('page_index', 1)
        page_size = request.GET.get('page_size', 10)
        category = request.GET.get('category', '')
        sku_name = request.GET.get('sku_name', '')
        bar_code = request.GET.get('bar_code', '')
        item_code = request.GET.get('item_code', '')
        paginator = SkuService().\
            list(user_id=user_id, page_size=page_size,
                 category=category, sku_name=sku_name,
                 item_code=item_code, bar_code=bar_code) 
        paginator.current_page = page
        paginator.serializer = SkuSerializer
        return JsonResponse(paginator, status=status.HTTP_200_OK)


# 获取商品详情
@api_view(['GET', 'POST', 'PATCH'])
@auth
def get_or_update(request, pk):
    user_id = request.user['id']
    if request.method == 'GET':
        sku = SkuService().get(user_id=user_id, sku_id=pk)
        serializer = SkuSerializer(sku)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    else:
        sku = SkuService().update(user_id=user_id, sku_id=pk, data=request.data)
        serializer = SkuSerializer(sku)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


# 删除商品
# 前置条件：
# 库存为空
@api_view(['DELETE', 'POST'])
@auth
def delete(request, pk):
    user_id = request.user['id']
    sku = SkuService().delete(user_id=user_id, sku_id=pk)
    serializer = SkuSerializer(sku)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


# 同步店铺商品
@api_view(['POST'])
@auth
def sync(request):
    result = SkuService().sync(request)
    return JsonResponse(data=result, status=status.HTTP_200_OK)
