from rest_framework.decorators import api_view
from oms_server.services.shared_warehouse_service import SharedWarehouseService
from oms_server.extension.auth_utils import auth
from oms_server.serializers.order_serializer import OrderSerializer
from oms_server.serializers.stock_in_serializer import StockInSerializer
from oms_server.serializers.sku_serializer import InvetorySerializer
from oms.extension.response_wrapper import JsonResponse


@api_view(['GET'])
@auth
def delivery_orders(request):
    ''' 发货任务 '''
    token = request.user['token']
    user_id = request.user['id']
    params = request.query_params
    page = int(params.get('page_index', 1))
    paginator = SharedWarehouseService().\
        delivery_orders(user_id=user_id, token=token, params=params)
    paginator.current_page = page
    paginator.serializer = OrderSerializer
    return JsonResponse(data=paginator)


@api_view(['GET'])
@auth
def entry_orders(request):
    ''' 入库任务 '''
    token = request.user['token']
    user_id = request.user['id']
    params = request.query_params
    page = params.get('page_index', 1)
    paginator = SharedWarehouseService().\
        entry_orders(user_id=user_id, token=token, params=params)
    paginator.current_page = page
    paginator.serializer = StockInSerializer
    return JsonResponse(data=paginator)


@api_view(['GET'])
@auth
def inventory(request):
    user_id = request.user['id']
    token = request.user['token']
    params = request.query_params
    warehouse_id = params.get('warehouse_id', None)
    page = int(params.get('page_index', 1))
    paginator = SharedWarehouseService().\
        list_warehouse_inventory(user_id=user_id, token=token,
                                 warehouse_id=warehouse_id,
                                 params=params)
    paginator.current_page = page
    paginator.serializer = InvetorySerializer
    return JsonResponse(data=paginator)
