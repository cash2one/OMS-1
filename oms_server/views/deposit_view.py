from rest_framework.decorators import api_view
from oms_server.services.deposit_service import DepositService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse
from oms_server.serializers.deposit_serializer import DepositDetailSerializer
from oms_server.serializers.withdraw_serializer import WithdrawSerializer
from oms_server.extension.format_utils import timestamp_to_datetime
from oms_server.extension.format_utils import get_today, get_tomorrow
from oms_server.extension.format_utils import get_yesterday


@api_view(['GET'])
@auth
def deposit(request):
    user_id = request.user['id']
    amount = DepositService().show_deposit(user_id=user_id)
    return JsonResponse(data={"amount": amount})


@api_view(['GET'])
@auth
def details(request):
    user_id = request.user['id']
    deposit_details = DepositService().\
        details(user_id=user_id)
    serializer = DepositDetailSerializer(deposit_details, many=True)
    return JsonResponse(data=serializer.data)


@api_view(['GET'])
@auth
def statistic(request):
    ''' ios专用接口 '''
    user_id = request.user['id']
    deposit_details = DepositService().\
        details(user_id=user_id)
    serializer = DepositDetailSerializer(deposit_details, many=True)
    result = {
        "rows": serializer.data}
    return JsonResponse(data=result)


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
    ch = DepositService().\
        charge(user_id=user_id, amount=amount, extra=extra,
               channel=channel, client_ip=client_ip)
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
    withdraw = DepositService().\
        withdraw(user_id=user_id, amount=amount,
                 channel=channel, recipient=recipient,
                 recipient_name=recipient_name)
    serializer = WithdrawSerializer(withdraw)
    return JsonResponse(data=serializer.data)

