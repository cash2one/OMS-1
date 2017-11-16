# -*- coding: utf-8 -*-
import logging
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.services.sku_category_service import SkuCategoryService
from oms_server.serializers.sku_category_serializer\
    import SkuCategorySerializer
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.auth_utils import auth

logger = logging.getLogger(__name__)


# 创建商品 和　获取商品列表
@api_view(['POST', 'GET'])
@auth
def create_or_list(request):
    user_id = request.user['id']
    if request.method == 'POST':
        sku_category = SkuCategoryService().\
            create(user_id=user_id,
                   data=request.data)
        serializer = SkuCategorySerializer(sku_category)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
    if request.method == 'GET':
        sku_categories = SkuCategoryService().\
            list(user_id=user_id)
        print(sku_categories)
        serializer = SkuCategorySerializer(sku_categories, many=True)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@auth
def get_or_update(request, pk):
    user_id = request.user['id']
    if request.method == 'POST':
        sku_category = SkuCategoryService().\
            update(user_id=user_id,
                   sku_category_id=pk, data=request.data)
        serializer = SkuCategorySerializer(sku_category)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'GET':
        sku_category = SkuCategoryService().\
            get(sku_category_id=pk,
                user_id=user_id)
        serializer = SkuCategorySerializer(sku_category)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@auth
def delete(request, pk):
    user_id = request.user['id']
    if request.method == 'POST':
        sku_category = SkuCategoryService().\
            delete(user_id=user_id,
                   sku_category_id=pk)
        serializer = SkuCategorySerializer(sku_category)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
