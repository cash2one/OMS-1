# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.auth_utils import auth
from oms_server.http_service.warehouse_service import list_available_warehouse
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms.extension.logger import time_logger


@api_view(['GET'])
@auth
@time_logger
def available_warehouses(request):
    token = request.user['token']
    result = list_available_warehouse(token)
    return JsonResponse(data=result)


@api_view(['GET'])
@auth
@time_logger
def warehouses(request, warehouse_id):
    token = request.user['token']
    result = get_warehouse_by_id(warehouse_id=warehouse_id, token=token)
    return JsonResponse(data=result)
