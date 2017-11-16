from rest_framework.decorators import api_view
from oms_server.services.balance_service import BalanceService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse
from oms_server.serializers.withdraw_serializer import\
    WithdrawSerializer
from oms_server.serializers.balance_serializer import\
    ReceiptDisbursenmentSerializer
from oms_server.extension.format_utils import timestamp_to_datetime
from oms_server.extension.format_utils import str_to_bool
from oms_server.extension.format_utils import get_today, get_tomorrow
from oms_server.extension.format_utils import get_yesterday


@api_view(['GET'])
@auth
def balance(request):
    user_id = request.user['id']
    amount = BalanceService().show_balance(user_id=user_id)
    return JsonResponse(data={"amount": amount})


@api_view(['GET'])
@auth
def recent(request):
    user_id = request.user['id']
    rds = BalanceService().recent(user_id=user_id)
    serializer = ReceiptDisbursenmentSerializer(rds, many=True)
    return JsonResponse(data=serializer.data)


@api_view(['GET'])
@auth
def details(request):
    ''' 余额明细区分WEB和IOS '''
    user_id = request.user['id']
    params = request.query_params
    statement_type = params.get('statement_type', None)
    is_receipt = str_to_bool(params.get('is_receipt', None))
    page = params.get('page_index', 1)
    page_size = params.get('page_size', 10)
    start_time = timestamp_to_datetime(params.get('start_time')) or get_yesterday()
    end_time = timestamp_to_datetime(params.get('end_time')) or get_tomorrow()
    UA = str.lower(request.META.get('HTTP_USER_AGENT', ''))
    if 'ios' in UA or 'iphone' in UA:
        paginator = BalanceService().\
            statistics_ios(user_id=user_id, statement_type=statement_type,
                           page_size=page_size, is_receipt=is_receipt)
    else:
        paginator = BalanceService().\
            statistics(user_id=user_id, statement_type=statement_type,
                       page_size=page_size, start_time=start_time,
                       is_receipt=is_receipt,
                       end_time=end_time)
    paginator.current_page = page
    paginator.serializer = ReceiptDisbursenmentSerializer
    return JsonResponse(data=paginator)


@api_view(['POST'])
@auth
def charge(request):
    user_id = request.user['id']
    data = request.data
    channel = data['channel']
    amount = data['amount']
    client_ip = data.get('client_ip', '127.0.0.1')
    extra = {}
    if channel == 'alipay_pc_direct':
        extra = dict(success_url=data['success_url'])
    ch = BalanceService().\
        charge_balance(user_id=user_id,
                       channel=channel,
                       amount=amount,
                       extra=extra,
                       client_ip=client_ip)
    return JsonResponse(data=ch)


@api_view(['POST'])
@auth
def withdraw(request):
    user_id = request.user['id']
    data = request.data
    amount = data['amount']
    channel = data['channel']
    recipient = data['recipient']
    recipient_name = data['recipient_name']
    withdraw = BalanceService().\
        withdraw_balance(user_id=user_id,
                         amount=amount,
                         channel=channel,
                         recipient=recipient,
                         recipient_name=recipient_name)
    serializer = WithdrawSerializer(withdraw)
    return JsonResponse(data=serializer.data)
    