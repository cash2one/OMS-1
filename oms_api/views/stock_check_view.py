# -*- coding: utf-8 -*-
from oms_api.services import stock_check_service
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse


@api_view(['POST'])
def stock_check(request):
    # params = param_utils.get_request_body(request.data)
    id = request.data.get('id')
    bar_code = request.data.get('bar_code')
    sku_name = request.data.get('sku_name')
    page_size = request.data.get('page_size')
    page_index = request.data.get('page_index')
    result = stock_check_service.stock_check(id, bar_code, sku_name, page_size, page_index)
    return JsonResponse(data=result)
