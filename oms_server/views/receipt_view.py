import datetime
from rest_framework.decorators import api_view
from oms_server.services.receipt_service import ReceiptService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse
from oms_server.extension.format_utils import get_today, get_tomorrow
from oms_server.extension.format_utils import get_yesterday
from oms_server.extension.format_utils import timestamp_to_datetime
from oms_server.serializers.receipt_serializer import OrderReceiptSerializer
from oms_server.serializers.receipt_serializer import StorgeReceiptSerializer


@api_view(['GET'])
@auth
def receipt(request):
    user_id = request.user['id']
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    amount = ReceiptService().receipt(user_id, year, month)
    return JsonResponse(data={'amount': amount})


@api_view(['GET'])
@auth
def statistics(request):
    user_id = request.user['id']
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    year = request.query_params.get('year', year)
    month = request.query_params.get('month', month)
    result = ReceiptService().receipt_statistics(user_id, year, month)
    return JsonResponse(data=result)


@api_view(['GET'])
@auth
def details(request):
    user_id = request.user['id']
    params = request.query_params
    receipt_type = params.get('receipt_type', 1)
    page = params.get('page_index', 1)
    page_size = params.get('page_size', 10)
    start_time = timestamp_to_datetime(params.get('start_time')) or get_yesterday()
    end_time = timestamp_to_datetime(params.get('end_time')) or get_tomorrow()
    serializer = OrderReceiptSerializer\
        if receipt_type == 1 else StorgeReceiptSerializer
    paginator = ReceiptService().\
        details(user_id, receipt_type=receipt_type,
                start_time=start_time, end_time=end_time,
                page_size=page_size)
    paginator.current_page = page
    paginator.serializer = serializer
    return JsonResponse(data=paginator)
