# -*- coding: utf-8 -*-
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.services.store_service import StoreService
from oms_server.serializers.store_serializer import StoreSerializer
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.auth_utils import auth

logger = logging.getLogger(__name__)


# 创建店铺
@api_view(['POST', 'GET'])
@auth
def create_or_list(request):
    user_id = request.user['id']
    if request.method == 'POST':
        store = StoreService().create(user_id=user_id, param=request.data)
        serializer = StoreSerializer(store)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'GET':
        user_id = request.user['id']
        page = request.GET.get('page_index', 1)
        page_size = request.GET.get('page_size', 10)
        paginator = StoreService().list(user_id=user_id, page_size=page_size)
        paginator.current_page = page
        paginator.serializer = StoreSerializer
        return JsonResponse(paginator, status=status.HTTP_200_OK)


# 更新店铺
@api_view(['GET', 'POST'])
@auth
def get_or_update(request, pk):
    user_id = request.user['id']
    if request.method == 'POST':
        store = StoreService().\
            update(user_id=user_id, store_id=pk, data=request.data)
        serializer = StoreSerializer(store)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'GET':
        user_id = request.user['id']
        store = StoreService().get(user_id=user_id, store_id=pk)
        serializer = StoreSerializer(store)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# 获取店铺列表
@api_view(['GET'])
@auth
def list(request):
    user_id = request.user['id']
    page = request.GET.get('page_index', 1)
    page_size = request.GET.get('page_size', 10)
    paginator = StoreService().list(user_id=user_id, page_size=page_size)
    paginator.current_page = page
    paginator.serializer = StoreSerializer
    return JsonResponse(paginator, status=status.HTTP_200_OK)


# 获取店铺详情
@api_view(['GET'])
@auth
def get(request, pk):
    user_id = request.user['id']
    store = StoreService().get(user_id=user_id, store_id=pk)
    serializer = StoreSerializer(store)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# 删除店铺
@api_view(['DELETE', 'POST'])
@auth
def delete(request, pk):
    user_id = request.user['id']
    store = StoreService().delete(user_id=user_id, store_id=pk)
    serializer = StoreSerializer(store)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
