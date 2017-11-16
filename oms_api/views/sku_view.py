# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse
from oms_api.services.sku_service import SkuService
from oms_api.services.inventory_service import InventoryService


@api_view(['POST'])
def lock_count(request):
    result = SkuService.lock_count(request.data)
    return JsonResponse(data=result)


@api_view(['POST'])
def create(request):
    result = SkuService.create(request.data)
    return JsonResponse(data=result)


@api_view(['GET'])
def list_all(request):
    sku_list = SkuService.list_all()
    result = sku_list
    return JsonResponse(data=result)


@api_view(['GET'])
def get(request):
    id = request.GET['id']
    sku = SkuService.get(id=id)
    result = sku
    return JsonResponse(data=result)


@api_view(['GET'])
def get_item_code(request):
    user_id = request.GET['user_id']
    item_code = request.GET['item_code']
    sku = SkuService.get_item_code(user_id=user_id, item_code=item_code)
    result = sku
    return JsonResponse(result)


@api_view(['GET'])
def get_count(request):
    item_code = request.GET['item_code']
    user_id = request.GET['user_id']
    warehouse_list = InventoryService.\
        sku_get_warehouse(user_id=user_id, item_code=item_code)
    result = warehouse_list
    return JsonResponse(data=result)


@api_view(['POST'])
def update(request):
    result = SkuService.update(request)
    return JsonResponse(data=result)
