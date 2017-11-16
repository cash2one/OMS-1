# -*- coding: utf-8 -*-
import time
import datetime
from rest_framework.decorators import api_view
from oms_api.services.store_service import StoreService
from oms.extension.response_wrapper import JsonResponse


@api_view(['GET'])
def get_store_numbers(request):
    count = StoreService.get_store_numbers()
    result = {'count': count}
    return JsonResponse(data=result)


@api_view(['GET'])
def get_list(request):
    page = request.GET.get('page_index')
    page_size = request.GET.get('page_size', 50)
    store_list = StoreService.get_list(page, page_size)
    stores = []
    for store in store_list:
        stores.append({
            'id': store.id,
            'user_id': store.user_id,
            'platform_id': store.platform.id,
            'platform_name': store.platform.name
        })
    result = stores
    return JsonResponse(data=result)


@api_view(['GET'])
def list(request):
    page = request.GET.get('page_index')
    page_size = request.GET.get('page_size', 10)
    store_list = StoreService.list(page, page_size)
    stores = []
    for store in store_list:
        stores.append({
            'id': store.id,
            'user_id': store.user_id,
            'platform_id': store.platform.id,
            'platform_name': store.platform.name
        })
    result = stores
    return JsonResponse(data=result)


@api_view(['GET'])
def get(request):
    store_id = request.GET.get('id')
    # TODO
    store = StoreService.get(store_id)

    if store.fetch_order_latest:
        dt = datetime.datetime.strftime(
            store.fetch_order_latest, '%Y-%m-%d %H:%M:%S')
    else:
        dt = None
    result = {
            'id': store.id,
            'store_name': store.store_name,
            'user_id': store.user_id,
            'access_token': store.access_token,
            'app_key': store.app_key,
            'app_secret': store.app_secret,
            'store_key': store.store_key,
            'platform_id': store.platform.id,
            'platform_name': store.platform.name,
            'last_get_order_at': dt,
            'store_is_auto_check': store.auto_check
        }
    result = result
    return JsonResponse(data=result)


@api_view(['POST'])
def set_last_get_order_at(request):
    id = request.data.get('id')
    ts = time.time()
    dt = datetime.datetime.\
        fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    result = StoreService.set_last_get_order_at(id, dt)
    return JsonResponse(data=result)


@api_view(['POST'])
def create(request):
    data = request.data
    result = StoreService.create(data)
    return JsonResponse(data=result)


@api_view(['GET'])
def list_all(request):
    store_list = StoreService.list_all()
    result = store_list
    return JsonResponse(data=result)
