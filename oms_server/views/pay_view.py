from rest_framework.decorators import api_view
from oms_server.services.charge_service import ChargeService
from oms_server.services.ping_callback_service import PingppCallbackService
from oms_server.extension.auth_utils import auth
from oms.extension.response_wrapper import JsonResponse


@api_view(['POST'])
@auth
def dev_auth_pay(request):
    ''' 开发者认证支付 '''
    # 余额明细看不见
    user_id = request.user['id']
    data = request.data
    pay_type = 4
    amount = 30000
    channel = data['channel']
    client_ip = data.get('client_ip', '127.0.0.1')
    extra = {}
    if channel == 'alipay_pc_direct':
        extra = dict(success_url=data['success_url'])
    ch = ChargeService().\
        pay(user_id=user_id, amount=amount, channel=channel,
            pay_type=pay_type, client_ip=client_ip, extra=extra)
    ChargeService().create_charge(ch=ch, pay_type=4, user_id=user_id)
    return JsonResponse(data=ch)


@api_view(['POST'])
def paid(request):
    ch = request.data
    result = PingppCallbackService().paid(ch)
    return JsonResponse(data=result)