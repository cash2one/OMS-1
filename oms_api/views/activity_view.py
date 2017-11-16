# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from oms_api.services.activity_service import ActivityService
from oms.extension.response_wrapper import JsonResponse


@api_view(['GET'])
def get(request):
    store_id = request.GET.get('store_id')
    result = ActivityService.get(store_id)
    return JsonResponse(data=result)
