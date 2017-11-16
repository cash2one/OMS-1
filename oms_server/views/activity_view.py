# -*- coding: utf-8 -*-
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from oms_server.serializers.activity_serializer\
    import ActivitySerializer, ActivityListSerializer
from oms_server.services.activity_service import ActivityService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse


# 创建活动 和　获取活动列表
@api_view(['POST', 'GET'])
@auth
def create_or_list(request):
    user_id = request.user['id']
    if request.method == 'POST':
        data = request.data
        request.data['begin_date'] = datetime.fromtimestamp(int(request.data.get('begin_date')))
        request.data['end_date'] = datetime.fromtimestamp(int(request.data.get('end_date')))
        store_ids = request.data.get('store_ids', [])
        activity_rules = ActivityService().\
            create(store_ids=store_ids, user_id=user_id, data=data)
        print(activity_rules)
        if isinstance(activity_rules, dict):
            serializer = activity_rules
            return JsonResponse(serializer, status=status.HTTP_201_CREATED)
        serializer = ActivityListSerializer(activity_rules, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'GET':
        page = request.GET.get('page_index', 1)
        page_size = request.GET.get('page_size', 10)
        paginator = ActivityService().\
            list(user_id=user_id, page=page, page_size=page_size)
        paginator.current_page = page
        paginator.serializer = ActivityListSerializer
        return JsonResponse(paginator, status=status.HTTP_200_OK)


# 获取活动详情或者编辑活动
@api_view(['GET', 'POST', 'PATCH', 'PUT'])
@auth
def get_or_update(request, pk):
    user_id = request.user['id']
    if request.method == 'GET':
        activity_rule = ActivityService().\
            get(user_id=user_id, activity_rule_id=pk)
        serializer = ActivitySerializer(activity_rule)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        request.data['begin_date'] = datetime.fromtimestamp(int(request.data.get('begin_date')))
        request.data['end_date'] = datetime.fromtimestamp(int(request.data.get('end_date')))
        activity_rule = ActivityService().\
            update(user_id=user_id, activity_rule_id=pk, data=request.data)
        serializer = ActivitySerializer(activity_rule)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# 开启/关闭活动
@api_view(['POST'])
@auth
def toggle(request, pk):
    user_id = request.user['id']
    acitivity_rule = ActivityService().\
        toggle_enable_activity(user_id=user_id, activity_rule_id=pk)
    serializer = ActivityListSerializer(acitivity_rule)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


# 删除活动
@api_view(['DELETE', 'POST'])
@auth
def delete(request, pk):
    user_id = request.user['id']
    acitivity_rule = ActivityService().\
        delete(user_id=user_id, activity_rule_id=pk)
    serializer = ActivityListSerializer(acitivity_rule)
    return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
