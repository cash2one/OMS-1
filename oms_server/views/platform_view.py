# -*- coding: utf-8 -*-
import logging
from rest_framework.decorators import api_view
from oms_server.services.platform_service import PlatformService
from oms_server.serializers.platform_serializer import PlatformSerializer
from oms.extension.response_wrapper import JsonResponse

logger = logging.getLogger(__name__)


# 创建平台 和　获取平台列表
@api_view(['POST', 'GET'])
def create_or_list(request):
    if request.method == 'POST':
        platform = PlatformService().create(data=request.data)
        serializer = PlatformSerializer(platform)
        return JsonResponse(serializer.data)
    if request.method == 'GET':
        platforms = PlatformService().list()
        serializer = PlatformSerializer(platforms, many=True)
        return JsonResponse(serializer.data)


# 获取平台详情
@api_view(['GET', 'POST', 'PATCH'])
def get_or_update(request, pk):
    if request.method == 'GET':
        pass
    else:
        pass


# 删除商品
# 前置条件：
# 库存为空
@api_view(['DELETE', 'POST'])
def delete(request, pk):
    pass
