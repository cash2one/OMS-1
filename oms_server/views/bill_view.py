# -*- coding: utf-8 -*-
import datetime
import json
from rest_framework.decorators import api_view
from oms.models.order import Order
from oms.models.order_express import OrderExpress
from oms.extension.response_wrapper import JsonResponse
from oms_server.services.bill_service import BillService
from oms_server.services.billing_service import BillingService
from oms_server.extension.auth_utils import auth
from oms_server.extension.format_utils import timestamp_to_datetime
from oms_server.extension.format_utils import get_today, get_tomorrow
from oms_server.serializers.bill_serializer import OrderBillSerializer
from oms_server.serializers.bill_serializer import StorgeBillSerializer


@api_view(['GET'])
@auth
def statistics(request):
    user_id = request.user['id']
    result = BillService().bill_statistics(user_id)
    return JsonResponse(result)


@api_view(['GET'])
@auth
def all_statistics(request):
    user_id = request.user['id']
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    year = request.query_params.get('year', year)
    month = request.query_params.get('month', month)
    result = BillService().total_bill_statistics(user_id, year, month)
    return JsonResponse(result)


@api_view(['GET'])
@auth
def details(request):
    user_id = request.user['id']
    params = request.query_params
    bill_type = int(params.get('bill_type', 1))
    page = int(params.get('page_index', 1))
    page_size = int(params.get('page_size', 10))
    start_time = timestamp_to_datetime(params.get('start_time')) or get_today()
    end_time = timestamp_to_datetime(params.get('end_time')) or get_tomorrow()
    serializer = OrderBillSerializer\
        if int(bill_type) == 1 else StorgeBillSerializer
    paginator = BillService().\
        details(user_id, bill_type=bill_type,
                start_time=start_time, end_time=end_time,
                page_size=page_size)
    paginator.current_page = page
    paginator.serializer = serializer
    return JsonResponse(data=paginator)


@api_view(['GET'])
@auth
def unsettle_statistics(request):
    user_id = request.user['id']
    result = BillService().unsettle_bill_statistics(user_id)
    return JsonResponse(result)


@api_view(['POST'])
@auth
def pay(request):
    user_id = request.user['id']
    data = request.data
    result = BillService().\
        pay(user_id=user_id, params=data)
    return JsonResponse(data=result)


@api_view(['POST'])
def test(request):
    order_id = request.data['order_id']
    order = Order.objects.get(id=order_id)

    logistics_code = request.data.get('logistics_code', 'ZTO')
    order_id = request.data['order_id']
    order_express = OrderExpress(
                    logistics_code=logistics_code,
                    logistics_name='申通快递',
                    express_code='ZTOO100021',
                    order_id=order_id,
                    length=1,
                    width=1,
                    height=1,
                    theoretical_weight=1,
                    weight=1,
                    volume=1,
                    invoice_No=1,
                )
    order_express.save()

    result = BillingService().order_billing(order, [order_express])
    print(result)
    return JsonResponse("success")


@api_view(['POST'])
def test_storge_bill(request):
    result = BillingService().storge_billing()
    print(result)
    return JsonResponse(data='Success')


@api_view(['GET'])
def test_overdue_bill(request):
    result = BillingService().overdue_billing()
    print(result)
    return JsonResponse(data='Success')


@api_view(['GET'])
def order_express(request):
    logistics_code = request.data.get('logistics_code', 'ZTO')
    order_id = request.data['order_id']
    order_express = OrderExpress(
                    logistics_code=logistics_code,
                    logistics_name='申通快递',
                    express_code='ZTOO100021',
                    order_id=order_id,
                    length=1,
                    width=1,
                    height=1,
                    theoretical_weight=1,
                    weight=1,
                    volume=1,
                    invoice_No=1,
                )
    order_express.save()
    return JsonResponse("success")


@api_view(['GET'])
def api(request):
    base = request.build_absolute_uri()
    result = {
        'statistics_url': base + 'statistics',
        'all_statistics_url': base + 'all_statistics',
        'details_url': base + 'details',
        'unsettle_statistics_url': base + 'unsettle_statistics',
        'pay_url': base + 'pay',
        'bill_type': {
            1: '发货账单',
            2: '仓储账单'
        }
    }
    return JsonResponse(data=result)

