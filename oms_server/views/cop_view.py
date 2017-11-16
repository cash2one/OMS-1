# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse


@api_view(['GET', 'POST'])
def cop(request):
    print("======================================")
    print(request.data)
    return JsonResponse(request.data, status=status.HTTP_200_OK)
