# -*- coding: utf-8 -*-
# from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse
from oms_server.services.operation_service import OperationService


@api_view(['GET'])
@auth
def shared_warehouse_info(request):
    token = request.META.get('HTTP_TOKEN')
    user_id = request.user['id']
    warehouse_id = request.GET.get('warehouse_id')
    return JsonResponse(
        OperationService.shared_warehouse_info(
            user_id=user_id, warehouse_id=warehouse_id, token=token))


@api_view(['GET'])
@auth
def used_warehouse_info(request):
    token = request.META.get('HTTP_TOKEN')
    user_id = request.user['id']
    warehouse_id = request.GET.get('warehouse_id')
    return JsonResponse(
        OperationService.used_warehouse_info(
            user_id=user_id, warehouse_id=warehouse_id, token=token))
