# -*- coding: utf-8 -*-
import json
from rest_framework.decorators import api_view
from oms_api.services.order_service import OrderService
from oms.extension.response_wrapper import JsonResponse
from oms.services.inventory_service import InventoryService


@api_view(['POST'])
def split_order(request):
    data = request.data.dict()
    order_id = data['order_id']
    split_orders = json.loads(data['split_orders'])
    result = OrderService.\
        split_order(order_id=order_id, split_orders=split_orders)
    return JsonResponse(data=result)


@api_view(['GET'])
def find_order(request):
    store_id = request.GET.get('store_id')
    order_mark = request.GET.get('order_mark')
    result = OrderService.find_order(store_id, order_mark)
    return JsonResponse(data=result)


@api_view(['POST', 'GET'])
def add(request):
    order = request.GET.get('order')
    js_order = json.loads(order)
    result = OrderService.create_order(js_order)
    return JsonResponse(data=result)


@api_view(['POST'])
def set_mark(request):
    order_code = request.data['order_code']
    store_id = request.data['store_id']
    reason = request.data['reason']
    mark = request.data['mark']
    result = OrderService.set_mark_tag(order_code, store_id, reason, mark)
    return JsonResponse(data=result)


@api_view(['GET'])
def get_detail(request):
    order_code = request.GET.get('order_code')
    store_id = request.GET.get('store_id')
    result = OrderService.get_detail(order_code, store_id)
    return JsonResponse(data=result)


@api_view(['POST'])
def set_status_ori(request):
    order_code = request.data['order_code']
    store_id = request.data['store_id']
    status_ori = request.data['status_ori']
    refund_status_ori = request.data['refund_status_ori']
    result = OrderService.\
        set_status_ori(order_code, store_id, status_ori, refund_status_ori)
    return JsonResponse(data=result)


@api_view(['POST'])
def set_status(request):
    order_code = request.data['order_code']
    store_id = request.data['store_id']
    status = request.data['status']
    result = OrderService.set_status(order_code, store_id, status)
    return JsonResponse(data=result)


@api_view(['POST'])
def add_skus(request):
    data = request.data['skus']
    datas = json.loads(data)
    result = OrderService.add_skus(datas)
    return JsonResponse(data=result)


@api_view(['POST'])
def examination_mannual(request):
    order = request.data
    result = OrderService.order_Examination(order)
    return JsonResponse(data=result)


@api_view(['POST'])
def set_warehouse(request):
    order_id = request.data['order_id']
    warehouse_id = request.data['warehouse_id']
    result = OrderService.\
        set_warehouse(order_id=order_id, warehouse_id=warehouse_id)
    return JsonResponse(data=result)


@api_view(['POST'])
def split_orders(request):
    order_id = request.data['order']
    warehouse_id = request.data['warehouse_id']
    result = OrderService.\
        set_warehouse(order_id=order_id, warehouse_id=warehouse_id)
    return JsonResponse(data=result)


@api_view(['POST'])
def lock_inventory(request):
    order_id = request.data['order_id']
    warehouse_id = request.data.get('warehouse_id', '0')
    return JsonResponse(
        InventoryService.lock_inventory(order_id, warehouse_id))
